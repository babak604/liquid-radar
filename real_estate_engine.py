def calculate_property_liquidity(region_name):
    """
    Evaluates geospatial capital velocity and structural risk factors 
    for major metropolitan basins. Optimized for Python 3.14+
    """
    region = region_name.strip()
    
    # Baseline macro variables for major regional basins
    macro_registry = {
        "Montreal Region": {
            "inventory_growth_yoy": 0.08,     # Stable single-digit expansion
            "building_permit_delta": -0.04,   # Slight institutional slowdown
            "rental_absorption_rate": 0.96,   # Extremely high demand insulating floor
            "base_safety": 74
        },
        "Greater Toronto Area": {
            "inventory_growth_yoy": 0.32,     # Rapid inventory accumulation
            "building_permit_delta": -0.18,   # Noticeable development pullback
            "rental_absorption_rate": 0.81,   # Cooling absorption
            "base_safety": 38
        },
        "Vancouver Metro": {
            "inventory_growth_yoy": 0.41,     # Aggressive supply surge
            "building_permit_delta": -0.29,   # Significant private equity pullback
            "rental_absorption_rate": 0.74,   # Sellers showing pricing fatigue
            "base_safety": 21
        }
    }
    
    data = macro_registry.get(region)
    if not data:
        return {"error": f"Region '{region}' outside monitored capital basins."}
        
    # Execution Logic: Calculate compression metrics
    inventory_stress = data["inventory_growth_yoy"] * 100
    absorption_deficit = (1.0 - data["rental_absorption_rate"]) * 100
    
    # Calculate a dynamic risk adjustment factor based on the supply/demand delta
    risk_variance = (inventory_stress + absorption_deficit) / 2
    calculated_safety = int(data["base_safety"] - (risk_variance * 0.1))
    calculated_safety = max(5, min(95, calculated_safety)) # Keep within logical bounds
    calculated_flight_score = 100 - calculated_safety

    # Structure localized tactical diagnostics
    if calculated_safety > 70:
        status = f"STABLE PATTERN: Strong rental demand ({int(data['rental_absorption_rate']*100)}%) and tight inventory controls are absorbing macro rate hikes."
        playbook = "🟢 Favorable window for strategic accumulation. Buyers hold localized leverage over specific pricing segments without capital floor degradation risk."
    elif calculated_safety > 35:
        status = f"LIQUIDITY COMPRESSION: Regional inventory levels are rising {int(inventory_stress)}% faster than new capital deployment."
        playbook = "🟡 High vulnerability to localized price adjustments. Hold off on highly leveraged acquisitions over the next 90 days."
    else:
        status = f"EVAPORATING FLOOR: Significant pullbacks observed in commercial and residential sectors. Supply growth outstripping capital velocity."
        playbook = "🔴 Extreme downside exposure. Sellers are flashing clear pricing fatigue. Prepare cash positions to acquire distressed liquidations over a longer time horizon."

    return {
        "Region": region,
        "Property Safety Index": f"{calculated_safety}%",
        "Capital Flight Score": f"{calculated_flight_score}%",
        "Condition": status,
        "Strategic Playbook": playbook
    }

if __name__ == "__main__":
    print("🏢 Testing Localized Geospatial Property Matrix...")
    local_metrics = calculate_property_liquidity("Montreal Region")
    print(f"\nRegion: {local_metrics['Region']}")
    print(f"Safety: {local_metrics['Property Safety Index']}")
    print(f"Diagnostics: {local_metrics['Condition']}")
