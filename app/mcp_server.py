# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("CeresMCPServer")


@mcp.tool()
def get_satellite_weather(lat: float, lon: float) -> str:
    """Get satellite-based weather conditions for a given GPS coordinate.

    Args:
        lat: Latitude of the location (decimal degrees).
        lon: Longitude of the location (decimal degrees).

    Returns:
        A JSON string describing current weather conditions at the coordinates.
    """
    weather_data = {
        "lat": lat,
        "lon": lon,
        "condition": "Heavy Rain",
        "warning": "Severe weather alert: Heavy rainfall expected in the next 6 hours. "
                   "Risk of localized flooding and reduced road visibility.",
        "temperature_c": 21,
        "humidity_pct": 88,
        "wind_speed_kmh": 45,
        "source": "Ceres Satellite Weather Network",
    }
    return json.dumps(weather_data, indent=2)


@mcp.tool()
def get_commodity_price(crop_id: str) -> str:
    """Get the current mock commodity market price per kilogram for a crop.

    Args:
        crop_id: A string identifier for the crop
                 (e.g., 'corn', 'wheat', 'soybeans', 'rice', 'cotton').

    Returns:
        A JSON string containing the crop ID, unit price in USD/kg,
        and the data source.
    """
    price_table = {
        "corn": 3,
        "wheat": 4,
        "soybeans": 5,
        "rice": 6,
        "cotton": 2,
        "sorghum": 3,
        "millet": 4,
    }
    price = price_table.get(crop_id.lower(), 4)
    result = {
        "crop_id": crop_id,
        "price_usd_per_kg": price,
        "currency": "USD",
        "source": "Ceres Commodity Exchange (mock)",
    }
    return json.dumps(result, indent=2)


@mcp.tool()
def get_vetted_buyers(location: str, crop: str) -> str:
    """Get a list of vetted buyers with their bids for a crop in a given location.

    Args:
        location: The region or city where the buyers are sourced from.
        crop: The crop type the buyers are interested in purchasing.

    Returns:
        A JSON list of 3 vetted buyers, each with a buyer_id, name,
        reliability rating, and bid price per kg.
    """
    # Derive a base price from the commodity price lookup
    price_table = {
        "corn": 3, "wheat": 4, "soybeans": 5,
        "rice": 6, "cotton": 2, "sorghum": 3, "millet": 4,
    }
    base_price = price_table.get(crop.lower(), 4)

    buyers = [
        {
            "buyer_id": "BUY-001",
            "buyer_name": f"{location.title()} Agricultural Cooperative",
            "reliability_rating": 4.9,
            "bid_price_per_kg": base_price + 1,
            "terms": "Immediate payment upon delivery",
        },
        {
            "buyer_id": "BUY-002",
            "buyer_name": f"Midwest Grain & Feed Ltd ({location.title()})",
            "reliability_rating": 4.7,
            "bid_price_per_kg": base_price,
            "terms": "30-day payment term",
        },
        {
            "buyer_id": "BUY-003",
            "buyer_name": "Valley Harvest Distributors",
            "reliability_rating": 4.5,
            "bid_price_per_kg": max(1, base_price - 1),
            "terms": "Flexible pickup options",
        },
    ]
    return json.dumps(buyers, indent=2)


@mcp.tool()
def book_freight(weight: float, location: str) -> str:
    """Book freight transport for a crop shipment from a given location.

    If the cargo weight exceeds 1000 kg, no trucks are available and
    the booking is rejected.

    Args:
        weight: The total cargo weight in kilograms.
        location: The pickup location (city or region name).

    Returns:
        A JSON object with the booking status, driver profile, and escrow ID,
        or an error message if weight exceeds capacity.
    """
    if weight > 1000:
        return json.dumps({"error": "ERROR: No trucks available"}, indent=2)

    freight_details = {
        "status": "booked",
        "escrow_id": "escrow_9876543210_xyz",
        "pickup_location": location,
        "cargo_weight_kg": weight,
        "driver_profile": {
            "driver_id": "DRV-4421",
            "name": "Jane Smith",
            "rating": 4.85,
            "phone_number": "+1-555-0100",
            "license_plate": "TX-HAUL-99",
            "vehicle_type": "Reefer Semi-Truck",
        },
    }
    return json.dumps(freight_details, indent=2)


@mcp.tool()
def find_warehouse_storage(location: str) -> str:
    """Find available warehouse storage near a given location.

    Args:
        location: The city or region to search for warehouse storage.

    Returns:
        A JSON object with the warehouse name, address, available capacity,
        and contact details.
    """
    warehouse = {
        "warehouse_name": f"{location.title()} Central Grain Storage",
        "address": f"Unit 12, AgriPark Industrial Estate, {location.title()}",
        "available_capacity_tonnes": 250,
        "storage_rate_usd_per_tonne_per_day": 1.50,
        "contact": {
            "name": "Robert Okafor",
            "phone": "+1-555-0199",
            "email": "storage@ceresgrain.io",
        },
    }
    return json.dumps(warehouse, indent=2)


@mcp.tool()
def create_escrow_payment(buyer_id: str, farmer_id: str, driver_id: str) -> str:
    """Create a secured escrow payment linking buyer, farmer, and driver.

    Funds are held in escrow and released to the farmer and driver
    once the buyer confirms receipt of the cargo.

    Args:
        buyer_id: The unique identifier of the buyer.
        farmer_id: The unique identifier of the farmer.
        driver_id: The unique identifier of the freight driver.

    Returns:
        A JSON object with the escrow contract ID, parties involved,
        status, and release conditions.
    """
    escrow = {
        "escrow_contract_id": f"ESC-{buyer_id}-{farmer_id}-{driver_id}",
        "status": "funded",
        "parties": {
            "buyer_id": buyer_id,
            "farmer_id": farmer_id,
            "driver_id": driver_id,
        },
        "release_condition": "Funds released to farmer and driver upon buyer confirmation of cargo receipt.",
        "platform_fee_pct": 1.5,
        "currency": "USD",
        "escrow_provider": "Ceres SecurePay (mock)",
    }
    return json.dumps(escrow, indent=2)


if __name__ == "__main__":
    mcp.run()
