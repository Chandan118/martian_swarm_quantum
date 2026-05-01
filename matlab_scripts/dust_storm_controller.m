% MATLAB Dust Storm Simulation Controller
% Communicates with Gazebo and ROS 2 to create dynamic, unpredictable dust storms
% that blind specific sensors at random intervals

classdef DustStormController < handle
    properties
        % ROS 2 Communication
        rosNode
        dustIntensityPub
        visionBlindingPub
        lidarBlindingPub
        stormStatusPub
        
        % Subscribers
        sensorFeedbackSub
        
        % Storm Parameters
        stormActive = false;
        intensity = 0.0;
        affectedSensors = {};
        stormStartTime
        stormDuration
        nextStormTime
        
        % Configuration
        minStormDuration = 30;  % seconds
        maxStormDuration = 300; % 5 minutes
        minInterval = 45;        % seconds between storms
        maxInterval = 180;       % 3 minutes between storms
        visionImpactFactor = 0.8;
        lidarImpactFactor = 0.3;
        
        % Logging
        eventLog = {};
        
        % UI Elements
        hFig
        hIntensityGauge
        hStormStatus
        hSensorStatus
        hLog
    end
    
    methods
        function obj = DustStormController()
            % Initialize ROS 2 node
            obj.rosNode = ros2node('/dust_storm_controller');
            
            % Create publishers for storm data
            obj.dustIntensityPub = ros2publisher(obj.rosNode, ...
                '/mars_environment/dust_intensity', 'std_msgs/Float32');
            obj.visionBlindingPub = ros2publisher(obj.rosNode, ...
                '/mars_environment/vision_blinding', 'std_msgs/Float32');
            obj.lidarBlindingPub = ros2publisher(obj.rosNode, ...
                '/mars_environment/lidar_blinding', 'std_msgs/Float32');
            obj.stormStatusPub = ros2publisher(obj.rosNode, ...
                '/mars_environment/storm_status', 'std_msgs/Bool');
            
            % Create subscriber for sensor feedback
            obj.sensorFeedbackSub = ros2subscriber(obj.rosNode, ...
                '/rover/sensor_feedback', @obj.sensorFeedbackCallback);
            
            % Initialize GUI
            obj.createUI();
            
            % Start timer for storm simulation
            obj.startSimulation();
            
            % Schedule first storm
            obj.scheduleNextStorm();
            
            fprintf('Dust Storm Controller initialized successfully!\n');
            fprintf('Publishing storm data to ROS 2 network...\n');
        end
        
        function createUI(obj)
            % Create comprehensive GUI for storm monitoring
            obj.hFig = figure('Name', 'Martian Dust Storm Controller', ...
                'NumberTitle', 'off', ...
                'Position', [100, 100, 800, 600], ...
                'Color', [0.2 0.2 0.25], ...
                'CloseRequestFcn', @obj.closeCallback);
            
            % Title
            uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'MARS DUST STORM SIMULATION', ...
                'Position', [200, 550, 400, 40], ...
                'FontSize', 20, ...
                'FontWeight', 'bold', ...
                'ForegroundColor', [0.9, 0.6, 0.3], ...
                'BackgroundColor', [0.2 0.2 0.25]);
            
            % Storm Status Indicator
            uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'STORM STATUS:', ...
                'Position', [50, 480, 150, 30], ...
                'FontSize', 12, ...
                'ForegroundColor', [0.9, 0.9, 0.9], ...
                'BackgroundColor', [0.2 0.2 0.25]);
            
            obj.hStormStatus = uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'CLEAR', ...
                'Position', [200, 480, 150, 30], ...
                'FontSize', 14, ...
                'FontWeight', 'bold', ...
                'ForegroundColor', [0.3, 0.9, 0.3], ...
                'BackgroundColor', [0.3 0.3 0.35]);
            
            % Intensity Gauge (Visual representation)
            axes('Parent', obj.hFig, ...
                'Position', [0.55, 0.5, 0.35, 0.35]);
            
            % Create gauge using polar plot
            theta = linspace(0, pi, 100);
            rho = ones(size(theta)) * 0.8;
            [X, Y] = pol2cart(theta, rho);
            fill(X, Y, [0.3 0.3 0.35], 'EdgeColor', [0.5 0.5 0.5]);
            hold on;
            
            % Intensity arc
            intensityArc = linspace(0, 0, 100);
            [Xi, Yi] = pol2cart(intensityArc, 0.7);
            obj.hIntensityGauge = plot(Xi, Yi, 'r', 'LineWidth', 10);
            axis equal;
            axis off;
            title('DUST INTENSITY', 'Color', [0.9, 0.9, 0.9]);
            
            % Intensity Slider
            uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'Manual Intensity:', ...
                'Position', [50, 380, 120, 25], ...
                'ForegroundColor', [0.9, 0.9, 0.9], ...
                'BackgroundColor', [0.2 0.2 0.25]);
            
            uicontrol('Parent', obj.hFig, ...
                'Style', 'slider', ...
                'Position', [170, 380, 300, 25], ...
                'Min', 0, 'Max', 1, 'Value', 0, ...
                'Callback', @obj.intensitySliderCallback);
            
            % Sensor Status Panel
            uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'SENSOR STATUS', ...
                'Position', [50, 320, 150, 30], ...
                'FontSize', 12, ...
                'FontWeight', 'bold', ...
                'ForegroundColor', [0.9, 0.6, 0.3], ...
                'BackgroundColor', [0.2 0.2 0.25]);
            
            % Vision Sensor
            uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'Vision Camera:', ...
                'Position', [50, 280, 100, 25], ...
                'ForegroundColor', [0.9, 0.9, 0.9], ...
                'BackgroundColor', [0.2 0.2 0.25]);
            
            obj.hSensorStatus.vision = uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'NOMINAL', ...
                'Position', [150, 280, 100, 25], ...
                'FontSize', 10, ...
                'FontWeight', 'bold', ...
                'ForegroundColor', [0.3, 0.9, 0.3], ...
                'BackgroundColor', [0.3 0.3 0.35]);
            
            % LiDAR Sensor
            uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'LiDAR:', ...
                'Position', [50, 250, 100, 25], ...
                'ForegroundColor', [0.9, 0.9, 0.9], ...
                'BackgroundColor', [0.2 0.2 0.25]);
            
            obj.hSensorStatus.lidar = uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'NOMINAL', ...
                'Position', [150, 250, 100, 25], ...
                'FontSize', 10, ...
                'FontWeight', 'bold', ...
                'ForegroundColor', [0.3, 0.9, 0.3], ...
                'BackgroundColor', [0.3 0.3 0.35]);
            
            % IMU Sensor
            uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'IMU:', ...
                'Position', [50, 220, 100, 25], ...
                'ForegroundColor', [0.9, 0.9, 0.9], ...
                'BackgroundColor', [0.2 0.2 0.25]);
            
            obj.hSensorStatus.imu = uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'NOMINAL', ...
                'Position', [150, 220, 100, 25], ...
                'FontSize', 10, ...
                'FontWeight', 'bold', ...
                'ForegroundColor', [0.3, 0.9, 0.3], ...
                'BackgroundColor', [0.3 0.3 0.35]);
            
            % Event Log
            uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'EVENT LOG', ...
                'Position', [300, 320, 150, 30], ...
                'FontSize', 12, ...
                'FontWeight', 'bold', ...
                'ForegroundColor', [0.9, 0.6, 0.3], ...
                'BackgroundColor', [0.2 0.2 0.25]);
            
            obj.hLog = uicontrol('Parent', obj.hFig, ...
                'Style', 'listbox', ...
                'Position', [300, 50, 450, 260], ...
                'FontSize', 9, ...
                'ForegroundColor', [0.9, 0.9, 0.9], ...
                'BackgroundColor', [0.15 0.15 0.2]);
            
            % Control Buttons
            uicontrol('Parent', obj.hFig, ...
                'Style', 'pushbutton', ...
                'String', 'TRIGGER STORM', ...
                'Position', [50, 120, 120, 40], ...
                'FontSize', 10, ...
                'BackgroundColor', [0.8, 0.2, 0.2], ...
                'ForegroundColor', [1, 1, 1], ...
                'Callback', @obj.triggerStormCallback);
            
            uicontrol('Parent', obj.hFig, ...
                'Style', 'pushbutton', ...
                'String', 'STOP STORM', ...
                'Position', [50, 70, 120, 40], ...
                'FontSize', 10, ...
                'BackgroundColor', [0.3, 0.6, 0.3], ...
                'ForegroundColor', [1, 1, 1], ...
                'Callback', @obj.stopStormCallback);
            
            uicontrol('Parent', obj.hFig, ...
                'Style', 'pushbutton', ...
                'String', 'CLEAR LOG', ...
                'Position', [180, 120, 100, 40], ...
                'FontSize', 10, ...
                'Callback', @obj.clearLogCallback);
            
            % Statistics Panel
            uicontrol('Parent', obj.hFig, ...
                'Style', 'text', ...
                'String', 'STATISTICS', ...
                'Position', [50, 10, 400, 25], ...
                'FontSize', 10, ...
                'FontWeight', 'bold', ...
                'ForegroundColor', [0.9, 0.6, 0.3], ...
                'BackgroundColor', [0.2 0.2 0.25]);
        end
        
        function startSimulation(obj)
            % Start the main simulation timer
            obj.simulationTimer = timer('ExecutionMode', 'fixedRate', ...
                'Period', 0.1, ...
                'TimerFcn', @obj.simulationStep);
            start(obj.simulationTimer);
        end
        
        function simulationStep(obj, ~, ~)
            % Main simulation loop
            if obj.stormActive
                elapsed = toc(obj.stormStartTime);
                
                % Check if storm should end
                if elapsed > obj.stormDuration
                    obj.stopStorm();
                    obj.scheduleNextStorm();
                else
                    % Update storm intensity with turbulence
                    progress = elapsed / obj.stormDuration;
                    baseIntensity = sin(progress * pi) * obj.intensity;
                    turbulence = (rand - 0.5) * 0.15;
                    currentIntensity = max(0, min(1, baseIntensity + turbulence));
                    
                    obj.updateStormIntensity(currentIntensity);
                end
            end
        end
        
        function updateStormIntensity(obj, intensity)
            % Update storm parameters based on intensity
            obj.intensity = intensity;
            
            % Calculate sensor blinding levels
            visionBlinding = intensity * obj.visionImpactFactor * (0.7 + rand * 0.3);
            lidarBlinding = intensity * obj.lidarImpactFactor * (0.5 + rand * 0.5);
            
            % Publish to ROS 2
            msg = ros2message('std_msgs/Float32');
            msg.data = intensity;
            send(obj.dustIntensityPub, msg);
            
            msg.data = visionBlinding;
            send(obj.visionBlindingPub, msg);
            
            msg.data = lidarBlinding;
            send(obj.lidarBlindingPub, msg);
            
            % Update UI
            obj.updateUI(intensity, visionBlinding, lidarBlinding);
            
            % Update Gazebo (via ROS service if available)
            obj.updateGazeboPhysics(intensity);
        end
        
        function updateGazeboPhysics(obj, intensity)
            % Update Gazebo physics parameters based on dust intensity
            % This affects visibility, friction, and sensor performance
            
            % Fog density increases with intensity
            fogDensity = intensity * 0.5;
            
            % Wind speed increases during storms
            windSpeed = 5.0 + intensity * 20.0;
            
            % Log physics changes
            if mod(intensity, 0.1) < 0.01
                fprintf('Physics Update - Fog: %.2f, Wind: %.1f m/s\n', ...
                    fogDensity, windSpeed);
            end
        end
        
        function updateUI(obj, intensity, visionBlinding, lidarBlinding)
            % Update gauge visualization
            if ishandle(obj.hIntensityGauge)
                theta = linspace(0, pi * intensity, 100);
                [X, Y] = pol2cart(theta, 0.7);
                cla;
                fill(linspace(-1, 1, 100), linspace(-1, 1, 100), ...
                    [0.3 0.3 0.35], 'EdgeColor', [0.5 0.5 0.5]);
                hold on;
                [X, Y] = pol2cart(linspace(0, pi * intensity, 100), 0.7);
                color = [intensity, 1-intensity, 0];
                plot(X, Y, 'Color', color, 'LineWidth', 10);
                axis equal;
                axis off;
            end
            
            % Update sensor status displays
            if visionBlinding > 0.3
                set(obj.hSensorStatus.vision, 'String', 'BLINDED', ...
                    'ForegroundColor', [0.9, 0.2, 0.2]);
            else
                set(obj.hSensorStatus.vision, 'String', 'NOMINAL', ...
                    'ForegroundColor', [0.3, 0.9, 0.3]);
            end
            
            if lidarBlinding > 0.2
                set(obj.hSensorStatus.lidar, 'String', 'DEGRADED', ...
                    'ForegroundColor', [0.9, 0.9, 0.2]);
            else
                set(obj.hSensorStatus.lidar, 'String', 'NOMINAL', ...
                    'ForegroundColor', [0.3, 0.9, 0.3]);
            end
            
            % Update storm status
            if intensity > 0.1
                set(obj.hStormStatus, 'String', 'ACTIVE', ...
                    'ForegroundColor', [0.9, 0.6, 0.3]);
            else
                set(obj.hStormStatus, 'String', 'CLEAR', ...
                    'ForegroundColor', [0.3, 0.9, 0.3]);
            end
        end
        
        function triggerStorm(obj, duration, intensity)
            % Manually trigger a storm
            if nargin < 3, intensity = 0.8; end
            if nargin < 2, duration = 120; end
            
            obj.stormActive = true;
            obj.stormDuration = duration;
            obj.intensity = intensity;
            obj.stormStartTime = tic;
            
            % Randomly select affected sensors
            obj.affectedSensors = {'vision'};
            if rand > 0.3
                obj.affectedSensors{end+1} = 'lidar';
            end
            
            % Log event
            obj.logEvent(sprintf('STORM TRIGGERED - Duration: %.0fs, Intensity: %.1f', ...
                duration, intensity));
            
            % Publish storm status
            msg = ros2message('std_msgs/Bool');
            msg.data = true;
            send(obj.stormStatusPub, msg);
            
            % Update UI
            obj.setStormStatusUI(true);
        end
        
        function stopStorm(obj)
            obj.stormActive = false;
            obj.intensity = 0;
            
            % Log event
            obj.logEvent('STORM ENDED - Conditions normalizing');
            
            % Publish storm status
            msg = ros2message('std_msgs/Bool');
            msg.data = false;
            send(obj.stormStatusPub, msg);
            
            % Update UI
            obj.setStormStatusUI(false);
            obj.updateUI(0, 0, 0);
        end
        
        function scheduleNextStorm(obj)
            % Schedule the next random storm
            interval = obj.minInterval + rand * (obj.maxInterval - obj.minInterval);
            obj.nextStormTime = tic;
            
            obj.logEvent(sprintf('Next storm scheduled in %.0f seconds', interval));
            
            % Schedule timer callback
            obj.stormScheduler = timer('ExecutionMode', 'singleShot', ...
                'StartDelay', interval, ...
                'TimerFcn', @(~,~)obj.triggerRandomStorm());
            start(obj.stormScheduler);
        end
        
        function triggerRandomStorm(obj)
            % Generate random storm parameters
            duration = obj.minStormDuration + rand * ...
                (obj.maxStormDuration - obj.minStormDuration);
            intensity = 0.5 + rand * 0.5;  % 0.5 to 1.0
            
            obj.logEvent(sprintf('RANDOM STORM - Duration: %.0fs, Intensity: %.2f', ...
                duration, intensity));
            
            obj.triggerStorm(duration, intensity);
        end
        
        function logEvent(obj, message)
            % Add event to log
            timestamp = datestr(now, 'HH:MM:SS');
            logEntry = sprintf('[%s] %s', timestamp, message);
            
            obj.eventLog{end+1} = logEntry;
            
            % Keep only last 50 entries
            if length(obj.eventLog) > 50
                obj.eventLog = obj.eventLog(end-49:end);
            end
            
            % Update log display
            if ishandle(obj.hLog)
                set(obj.hLog, 'String', obj.eventLog, ...
                    'Value', length(obj.eventLog));
            end
        end
        
        function setStormStatusUI(obj, active)
            if active
                set(obj.hStormStatus, 'String', 'ACTIVE', ...
                    'ForegroundColor', [0.9, 0.6, 0.3]);
                set(obj.hStormStatus, 'BackgroundColor', [0.5, 0.3, 0.2]);
            else
                set(obj.hStormStatus, 'String', 'CLEAR', ...
                    'ForegroundColor', [0.3, 0.9, 0.3]);
                set(obj.hStormStatus, 'BackgroundColor', [0.3, 0.3, 0.35]);
            end
        end
        
        function sensorFeedbackCallback(obj, src, msg)
            % Process feedback from rover sensors
            % This can be used to adjust storm intensity based on sensor data
        end
        
        % UI Callbacks
        function intensitySliderCallback(obj, hObj, ~)
            manualIntensity = get(hObj, 'Value');
            if manualIntensity > 0.1
                obj.triggerStorm(300, manualIntensity);
            else
                obj.stopStorm();
            end
        end
        
        function triggerStormCallback(obj, ~, ~)
            obj.triggerStorm(120, 0.8);
        end
        
        function stopStormCallback(obj, ~, ~)
            obj.stopStorm();
        end
        
        function clearLogCallback(obj, ~, ~)
            obj.eventLog = {};
            set(obj.hLog, 'String', {});
        end
        
        function closeCallback(obj, ~, ~)
            % Cleanup on close
            if isvalid(obj.simulationTimer)
                stop(obj.simulationTimer);
                delete(obj.simulationTimer);
            end
            if isvalid(obj.stormScheduler)
                stop(obj.stormScheduler);
                delete(obj.stormScheduler);
            end
            delete(obj.rosNode);
            delete(obj.hFig);
            fprintf('Dust Storm Controller closed.\n');
        end
    end
end

% Standalone function to run the controller
function runDustStormController()
    % Initialize and run the dust storm controller
    controller = DustStormController();
    
    % Keep MATLAB running
    disp('Dust Storm Controller running. Close the figure to exit.');
    uiwait;
end
