import Setups as s
import pandas as pd

def Heat_Up():
	"""
    Perform the heating process.
    This function heats up a system by activating a solenoid, maintaining pressure, and
    collecting temperature data for a specific duration.
    Steps:
    1. Activate the solenoid to start the heating process.
    2. Maintain pressure until it reaches a threshold (10 in this case).
    3. Record temperature data and control a relay based on a counter for a certain number of loops.
    4. The process continues until a specified number of loops is completed.
    """
	print("Heating Up!")
	s.sol.value = True
	while s.pressure < 10:
		s.pressure = s.raw_pressure = (((s.chan.value*.000125) - .506)*4)
		#print(s.pressure)
		s.pumpOn = True
	s.pumpOn = False
	s.endTime = s.time.time() + (180)
	s.startTime = s.time.time()
	s.heat_up_flag = True
	while s.heat_up_flag is True:
		if s.loops > 10:
			#print('Temp: {}  CPS: {}  Elap Time: {}'.format(s.temp_list[s.loops-1], s.cps_T, s.elapsedTime))
			s.temp = s.thermocouple.temperature
			Set_CPS_T()
			s.elapsedTime = s.time.time() - s.startTime
			s.temp_list.append(s.temp)
			s.elapsedTime_list.append(s.elapsedTime)
			while s.click < 100:
				if s.counter < s.cps_T:
					s.rel.value = True
				else:
					s.rel.value = False	
				s.counter+=1
				s.click+=1
				
			s.counter = 0
			s.click = 0
			s.loops += 1
			print(s.temp)
		if s.loops <= 10:
			s.temp = s.thermocouple.temperature
			s.temp_list.append(s.temp)
			s.elapsedTime = s.time.time() - s.startTime
			s.elapsedTime_list.append(s.elapsedTime)
			s.loops += 1
			#print('loops under 10')
	s.pumpOn = False
	
def Purge():
	"""
    Perform a purge operation.
    This function activates a pump and maintains a target temperature for a specified duration
    to purge the system.
    Steps:
    1. Set the relay value to False.
    2. Activate the pump and maintain temperature for 5 seconds (adjustable).
    3. Deactivate the pump after the specified duration.
    This function relies on the 'Maintain_Temp' function to control temperature during the purge.
    """
	purge_time = s.time.time() + 5
	s.rel.value = False
	while s.time.time() < purge_time:
		Maintain_Temp()
		s.pumpOn = True
	s.pumpOn = False
	
def Infuse():
	"""
    Perform the infusion process.
    This function infuses the system with a substance, controlling temperature and collecting
    data for analysis.
    Steps:
    1. Set up flags and variables for the infusion process.
    2. Collect temperature data, control relay, and maintain temperature until the target is reached.
    3. Start a thread to continuously monitor temperature.
    4. Begin the main loop, maintaining temperature, and collecting data.
    """
	s.infuse_flag = True
	while s.temp < s.targ_temp:
		if s.loops > 10:
			s.temp = s.thermocouple.temperature
			Set_CPS_T()
			s.elapsedTime = s.time.time() - s.startTime
			s.temp_list.append(s.temp)
			s.elapsedTime_list.append(s.elapsedTime)
			while s.click < 100:
				if s.counter < s.cps_T:
					s.rel.value = True
				else:
					s.rel.value = False	
				s.counter+=1
				s.click+=1
				
			s.counter = 0
			s.click = 0
			s.loops += 1
			print(s.temp)
	
	loop_start = 0
	s.temp_list.clear()
	s.elapsedTime_list.clear()
	s.loops = 0
	temp = s.Thread(target = Get_Temp)
	temp.start()
	s.sol.value = False
	s.prev_loop_time = s.time.time()
	Begin_Timer()
	while s.time.time() <= s.endTime:
		Maintain_Temp()
		loop_start = s.time.time()
		Get_Pressure()
		Get_Weight()
		Set_CPS_P()
		Set_CPS_T()
		s.elapsedTime = s.time.time() - s.startTime
		Append_Lists()
		s.loop_end += s.time.time() - loop_start
		while s.click < 100:  
			if s.counter < s.cps:
				s.pumpOn = True
			else:
				s.pumpOn = False
				
			if s.counter < s.cps_T:
				s.rel.value = True
			else:
				s.rel.value = False
				
			
			s.counter+=1
			s.click+=1
		s.counter = 0
		s.click = 0
		s.loops += 1
	print('Avg loop time: {}'.format(s.loop_end/s.loops))
	Retrieve_Data()
	
def Get_Temp():
	"""
    Continuously monitor and update the temperature.
    This function retrieves temperature data from a thermocouple in a loop until the specified end time.
    This function is typically used as a thread to continuously monitor temperature during certain processes.
    """
	k = 0
	while s.time.time() < s.endTime:
		try:
			s.temp = s.thermocouple.temperature
			k += 1
		except:
			pass	
	
def Get_Weight():
	"""
    Retrieve and process weight data.
    This function retrieves weight data from a sensor, processes it, and updates the global weight variable.
    Steps:
    1. Retrieve raw weight data and convert it to grams.
    2. Apply filtering to ensure smooth weight updates.
    3. Update the global weight variable.
    This function is designed to handle exceptions and set weight to 0 if an error occurs.
    """
	try:
		w = (s.hx.get_value(1)/s.raw_to_gram)
		if w > s.weight_list[s.loops-1] + 1:
			w = s.weight_list[s.loops-1] + 1
		if w < s.weight_list[s.loops-1] - 1:
			w = s.weight_list[s.loops-1] - 1
		s.weight = (s.np.exp(-.105)*s.weight_list[s.loops-1] + w*.1)
		print(s.weight)
	except:
		s.weight = 0 
				
def Maintain_Temp():
	"""
    Maintain the target temperature.
    This function adjusts the control parameter for temperature to ensure it stays within acceptable bounds.
    Steps:
    1. Set the control parameter for temperature (CPS_T).
    2. Ensure CPS_T is within a specific range.
    3. If CPS_T is greater than 100, set it to 100. If it is less than or equal to 0, set it to 1.
    """
	Set_CPS_T()
	if s.cps_T > 100:
		s.cps_T = 100
	if s.cps_T <= 0:
		s.cps_T = 1
		
def Get_Pressure():
	"""
    Retrieve and update pressure data.
    This function calculates the pressure based on raw sensor data and updates global pressure variables.
    Steps:
    1. If loops are greater than 0, apply exponential filtering to the pressure data.
    2. If loops are 0, set pressure and previous pressure directly based on raw sensor data.
    """
	print('Loops is: {}'.format(s.loops))
	if s.loops > 0:
		s.raw_pressure = (((s.chan.value*.000125) - .506)*4)
		#s.pressure = s.np.exp(-.02)*s.pressure_list[s.loops-1]+.02*s.raw_pressure
		s.pressure = s.np.exp(-.02)*s.prev_pressure +.02*s.raw_pressure
		s.prev_pressure = s.pressure
	else:
		s.pressure = (((s.chan.value*.000125) - .506)*4)
		s.prev_pressure = s.pressure
					
def Set_CPS_P():
	"""
    Set the control parameter for pressure (CPS).
    This function adjusts the control parameter for pressure and ensures it stays within acceptable bounds.
    Steps:
    1. Apply a Proportional-Derivative (PD) control algorithm to adjust CPS.
    2. Ensure CPS is within a specific range.
    3. If CPS is greater than 100, set it to 100. If it is less than or equal to 0, set it to 1.
    """
	s.cps = PD_CPS(s.cps)
	if s.cps > 100:
		s.cps = 100
	if s.cps <= 0:
		s.cps = 1

def Set_CPS_T():
	"""
    Set the control parameter for temperature (CPS_T).
    This function adjusts the control parameter for temperature and ensures it stays within acceptable bounds.
    Steps:
    1. Apply a Proportional-Derivative (PD) control algorithm to adjust CPS_T.
    2. Ensure CPS_T is within a specific range.
    3. If CPS_T is greater than 100, set it to 100. If it is less than or equal to 0, set it to 1.
    """
	s.cps_T = PD_Temp(s.cps_T)
	if s.cps_T > 100:
		s.cps_T = 100
	if s.cps_T <= 0:
		s.cps_T = 1
		
def PD_CPS(cps):
	"""
    Proportional-Derivative (PD) control algorithm for adjusting CPS.
    This function calculates the change in CPS based on the error and its derivative.
    Args:
        cps (float): Current control parameter for pressure.
    Returns:
        float: New control parameter for pressure after applying the PD control algorithm.
    """
	kp = 1.9
	kd = .4
	delta_t = s.time.time() - s.prev_loop_time_P
	try:
		pd_dot = (s.profile.getPressureTarg(s.elapsedTime + delta_t) - s.profile.getPressureTarg(s.elapsedTime))/delta_t
		p_dot = (s.pressure - s.pressure_list[s.loops - 1])/delta_t
		e = s.profile.getPressureTarg(s.elapsedTime) - s.pressure
		e_dot = pd_dot - p_dot
		s.delta_cps = (kp*e) + (kd*e_dot)
		new_cps = cps + s.delta_cps
		s.prev_loop_time_P = s.time.time()
		return new_cps
	except:
		s.prev_loop_time_P = s.time.time()
		return s.cps
		
def PD_Temp(cps_T):
	"""
    Proportional-Derivative (PD) control algorithm for adjusting CPS_T based on temperature.
    This function calculates the change in CPS_T based on the error and its derivative.
    Args:
        cps_T (float): Current control parameter for temperature.
    Returns:
        float: New control parameter for temperature after applying the PD control algorithm.
    """
	if s.heat_up_flag is True:
		kp = 6
		kd = 12
	else:
		kp = 6
		kd = 12
	delta_t = .09 # 90 ms sampling rate
	try:
		pd_dot = 0
		p_dot = (s.temp - s.temp_list[s.loops - 1])/delta_t
		e = s.targ_temp - s.temp
		e_dot = pd_dot - p_dot
		s.delta_cps_T = (kp*e) + (kd*e_dot)
		new_cps = cps_T + s.delta_cps_T
		return new_cps 
	except:
		return s.cps_T
		
def Append_Lists():
	"""
    Append data to various lists for logging and analysis.
    This function appends data related to weight, pressure, control parameters, elapsed time, and temperature
    to their respective lists.
    """
	s.weight_list.append(s.weight)
	if s.elapsedTime < s.profile.time.max():
		s.expected_pressure_list.append(s.profile.getPressureTarg(s.elapsedTime))
	s.pressure_list.append(s.pressure)
	s.raw_pressure_list.append(s.raw_pressure)
	s.cps_list.append(s.cps)
	s.cps_temp_list.append(s.cps_T)
	s.delta_cps_list.append(s.delta_cps) 
	s.delta_cps_list_T.append(s.delta_cps_T)
	s.elapsedTime_list.append(s.elapsedTime)
	s.temp_list.append(s.temp)
	#print(s.elapsedTime, s.weight)
	
def Retrieve_Data():
	"""
    Retrieve data and save it to a CSV file.
    This function creates a DataFrame from collected data and saves it to a CSV file.
    """
	dict = {'Temp': s.temp_list, 'Elapsed Time': s.elapsedTime_list}
	df = pd.DataFrame(dict)
	df.to_csv('/home/centrepolis/Desktop/Temp CSV/test1.csv')
	
def Begin_Timer():
	"""
    Begin the timer for the process.
    This function initializes the start time and end time for the process based on the provided profile.
    """
	s.startTime = s.time.time()
	#s.preinfuseTime = s.time.time() + preInfuseTime
	s.endTime = s.time.time() + s.profile.time.max()
