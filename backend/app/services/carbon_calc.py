def calculate_energy_co2(ac_hours: float, roommates: int, shared_kwh: float = 0.0) -> float:
    """
    Calculates the Carbon Dioxide Equivalent (CO2e) for energy usage.
    
    Args:
        ac_hours (float): Hours of AC usage.
        roommates (int): Number of roommates sharing the space.
        shared_kwh (float): Shared appliance energy consumption in kWh. Defaults to 0.0.
        
    Returns:
        float: Calculated CO2e rounded to 3 decimal places.
    """
    co2 = ((ac_hours * 1.5 * 0.82) / roommates) + ((shared_kwh * 0.82) / roommates)
    return round(co2, 3)


def calculate_transit_co2(distance: float, mode: str, passengers: int) -> float:
    """
    Calculates the Carbon Dioxide Equivalent (CO2e) for transit.
    
    Args:
        distance (float): Distance traveled.
        mode (str): Transport mode ('rickshaw', 'shuttle', 'two_wheeler', etc.).
        passengers (int): Number of passengers.
        
    Returns:
        float: Calculated CO2e rounded to 3 decimal places.
    """
    factors = {
        "rickshaw": 0.05,
        "shuttle": 0.02,
        "two_wheeler": 0.10
    }
    
    # Fallback to 0.0 for unknown modes like 'walking'
    factor = factors.get(mode, 0.0)
    co2 = (distance * factor) / passengers
    
    return round(co2, 3)


def calculate_waste_co2(grams: float) -> float:
    """
    Calculates the Carbon Dioxide Equivalent (CO2e) for food waste.
    
    Args:
        grams (float): Weight of the waste in grams.
        
    Returns:
        float: Calculated CO2e rounded to 3 decimal places.
    """
    co2 = grams * 0.002
    return round(co2, 3)
