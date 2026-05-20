from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.cultiva_lab.exceptions import (CropTypeNotFoundError,
                                        ResourceOwnershipError,
                                        InvalidInputError,
                                        DuplicateDataError,
                                        BusinessRuleViolationError,
                                        UserNotFoundError)
from ..schemas.crop_type import CropTypeResponse, CropTypeCreateRequest, CropTypeUpdateRequest
from ..dependencies import get_current_user, get_crop_type_service, get_current_admin_user

router = APIRouter(prefix = "/crop-types", tags = ["Crop Types"])

@router.get("/", response_model=List[CropTypeResponse])
def get_crop_types(crop_type_service = Depends(get_crop_type_service)):
    types = crop_type_service.get_crop_types()
    return [CropTypeResponse(
        id=t.id,
        name=t.name,
        optimal_temp=t.optimal_temp,
        minimum_temp=t.minimum_temp,
        maximum_temp=t.maximum_temp,
        cold_sensibility=t.cold_sensibility,
        heat_sensibility=t.heat_sensibility,
        cold_factor=t.cold_factor,
        heat_factor=t.heat_factor,
        water_wilting=t.water_wilting,
        water_opt_low=t.water_opt_low,
        needed_water=t.needed_water,
        water_opt_high=t.water_opt_high,
        water_capacity=t.water_capacity,
        water_sensibility=t.water_sensibility,
        needed_light=t.needed_light,
        needed_light_max=t.needed_light_max,
        light_sensibility=t.light_sensibility,
        light_km=t.light_km,
        phenological_initial_coefficient=t.phenological_initial_coefficient,
        phenological_mid_coefficient=t.phenological_mid_coefficient,
        phenological_end_coefficient=t.phenological_end_coefficient,
        days_cycle=t.days_cycle,
        growth_breathing_coefficient=t.growth_breathing_coefficient,
        photosyntesis_max_rate=t.photosyntesis_max_rate,
        breathing_base_rate=t.breathing_base_rate,
        consecutive_stress_days_limit=t.consecutive_stress_days_limit,
        activation_energy=t.activation_energy,
        initial_biomass=t.initial_biomass,
        potential_performance=t.potential_performance
    ) for t in types]

@router.get("/{crop_type_id}", response_model=CropTypeResponse)
def get_crop_type_by_id(crop_type_id: str, crop_type_service = Depends(get_crop_type_service)):
    try:
        crop_type = crop_type_service.get_crop_type_by_id(crop_type_id)
        return CropTypeResponse(
            id=crop_type.id,
            name=crop_type.name,
            optimal_temp=crop_type.optimal_temp,
            minimum_temp=crop_type.minimum_temp,
            maximum_temp=crop_type.maximum_temp,
            cold_sensibility=crop_type.cold_sensibility,
            heat_sensibility=crop_type.heat_sensibility,
            cold_factor=crop_type.cold_factor,
            heat_factor=crop_type.heat_factor,
            temperature_curve_length=crop_type.temperature_curve_length,
            water_wilting=crop_type.water_wilting,
            water_opt_low=crop_type.water_opt_low,
            needed_water=crop_type.needed_water,
            water_opt_high=crop_type.water_opt_high,
            water_capacity=crop_type.water_capacity,
            water_sensibility=crop_type.water_sensibility,
            water_stress_constant=crop_type.water_stress_constant,
            needed_light=crop_type.needed_light,
            needed_light_max=crop_type.needed_light_max,
            light_sensibility=crop_type.light_sensibility,
            light_km=crop_type.light_km,
            light_sigma=crop_type.light_sigma,
            phenological_initial_coefficient=crop_type.phenological_initial_coefficient,
            phenological_mid_coefficient=crop_type.phenological_mid_coefficient,
            phenological_end_coefficient=crop_type.phenological_end_coefficient,
            days_cycle=crop_type.days_cycle,
            photosyntesis_max_rate=crop_type.photosyntesis_max_rate,
            breathing_base_rate=crop_type.breathing_base_rate,
            growth_breathing_coefficient=crop_type.growth_breathing_coefficient,
            theta=crop_type.theta,
            consecutive_stress_days_limit=crop_type.consecutive_stress_days_limit,
            theta_coefficient=crop_type.theta_coefficient,
            activation_energy=crop_type.activation_energy,
            initial_biomass=crop_type.initial_biomass,
            potential_performance=crop_type.potential_performance
        )
    except CropTypeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=CropTypeResponse, status_code=status.HTTP_201_CREATED)
def create_crop_type(request: CropTypeCreateRequest, current_user: dict = Depends(get_current_admin_user), crop_type_service = Depends(get_crop_type_service)):
    try:
        crop_type = crop_type_service.create_crop_type(
            admin_id=current_user["id"],
            name=request.name,
            optimal_temp=request.optimal_temp,
            minimum_temp=request.minimum_temp,
            maximum_temp=request.maximum_temp,
            cold_sensibility=request.cold_sensibility,
            heat_sensibility=request.heat_sensibility,
            cold_factor=request.cold_factor,
            heat_factor=request.heat_factor,
            temperature_curve_length=request.temperature_curve_length,
            water_wilting=request.water_wilting,
            water_opt_low=request.water_opt_low,
            needed_water=request.needed_water,
            water_opt_high=request.water_opt_high,
            water_capacity=request.water_capacity,
            water_sensibility=request.water_sensibility,
            water_stress_constant=request.water_stress_constant,
            needed_light=request.needed_light,
            needed_light_max=request.needed_light_max,
            light_sensibility=request.light_sensibility,
            light_km=request.light_km,
            light_sigma=request.light_sigma,
            phenological_initial_coefficient=request.phenological_initial_coefficient,
            phenological_mid_coefficient=request.phenological_mid_coefficient,
            phenological_end_coefficient=request.phenological_end_coefficient,
            days_cycle=request.days_cycle,
            photosyntesis_max_rate=request.photosyntesis_max_rate,
            breathing_base_rate=request.breathing_base_rate,
            growth_breathing_coefficient=request.growth_breathing_coefficient,
            theta=request.theta,
            consecutive_stress_days_limit=request.consecutive_stress_days_limit,
            theta_coefficient=request.theta_coefficient,
            activation_energy=request.activation_energy,
            initial_biomass=request.initial_biomass,
            potential_performance=request.potential_performance,
        )
        return CropTypeResponse(
            id=crop_type.id,
            name=crop_type.name,
            optimal_temp=crop_type.optimal_temp,
            minimum_temp=crop_type.minimum_temp,
            maximum_temp=crop_type.maximum_temp,
            cold_sensibility=crop_type.cold_sensibility,
            heat_sensibility=crop_type.heat_sensibility,
            cold_factor=crop_type.cold_factor,
            heat_factor=crop_type.heat_factor,
            water_wilting=crop_type.water_wilting,
            water_opt_low=crop_type.water_opt_low,
            needed_water=crop_type.needed_water,
            water_opt_high=crop_type.water_opt_high,
            water_capacity=crop_type.water_capacity,
            water_sensibility=crop_type.water_sensibility,
            needed_light=crop_type.needed_light,
            needed_light_max=crop_type.needed_light_max,
            light_sensibility=crop_type.light_sensibility,
            light_km=crop_type.light_km,
            phenological_initial_coefficient=crop_type.phenological_initial_coefficient,
            phenological_mid_coefficient=crop_type.phenological_mid_coefficient,
            phenological_end_coefficient=crop_type.phenological_end_coefficient,
            days_cycle=crop_type.days_cycle,
            growth_breathing_coefficient = crop_type.growth_breathing_coefficient,
            photosyntesis_max_rate=crop_type.photosyntesis_max_rate,
            breathing_base_rate=crop_type.breathing_base_rate,
            consecutive_stress_days_limit=crop_type.consecutive_stress_days_limit,
            activation_energy=crop_type.activation_energy,
            initial_biomass=crop_type.initial_biomass,
            potential_performance=crop_type.potential_performance,
        )
    except (InvalidInputError, DuplicateDataError, ResourceOwnershipError, UserNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{crop_type_id}", response_model=CropTypeResponse)
def update_crop_type(
    crop_type_id: str, 
    request: CropTypeUpdateRequest, 
    current_user: dict = Depends(get_current_admin_user), 
    crop_type_service = Depends(get_crop_type_service)
):
    try:
        updates = request.dict(exclude_unset=True)
        updated = crop_type_service.update_crop_type(current_user["id"], crop_type_id, **updates)
        return CropTypeResponse(
            id=updated.id,
            name=updated.name,
            optimal_temp=updated.optimal_temp,
            minimum_temp=updated.minimum_temp,
            maximum_temp=updated.maximum_temp,
            cold_sensibility=updated.cold_sensibility,
            heat_sensibility=updated.heat_sensibility,
            cold_factor=updated.cold_factor,
            heat_factor=updated.heat_factor,
            temperature_curve_length=updated.temperature_curve_length,
            water_wilting=updated.water_wilting,
            water_opt_low=updated.water_opt_low,
            needed_water=updated.needed_water,
            water_opt_high=updated.water_opt_high,
            water_capacity=updated.water_capacity,
            water_sensibility=updated.water_sensibility,
            water_stress_constant=updated.water_stress_constant,
            needed_light=updated.needed_light,
            needed_light_max=updated.needed_light_max,
            light_sensibility=updated.light_sensibility,
            light_km=updated.light_km,
            light_sigma=updated.light_sigma,
            phenological_initial_coefficient=updated.phenological_initial_coefficient,
            phenological_mid_coefficient=updated.phenological_mid_coefficient,
            phenological_end_coefficient=updated.phenological_end_coefficient,
            days_cycle=updated.days_cycle,
            photosyntesis_max_rate=updated.photosyntesis_max_rate,
            breathing_base_rate=updated.breathing_base_rate,
            growth_breathing_coefficient=updated.growth_breathing_coefficient,
            theta=updated.theta,
            consecutive_stress_days_limit=updated.consecutive_stress_days_limit,
            theta_coefficient=updated.theta_coefficient,
            activation_energy=updated.activation_energy,
            initial_biomass=updated.initial_biomass,
            potential_performance=updated.potential_performance
        )
    except (CropTypeNotFoundError, BusinessRuleViolationError, InvalidInputError, ResourceOwnershipError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{crop_type_id}")
def delete_crop_type(crop_type_id: str, current_user: dict = Depends(get_current_admin_user), crop_type_service = Depends(get_crop_type_service)):
    try:
        crop_type_service.delete_crop_type(current_user["id"], crop_type_id)
        return {"message": "Crop type deleted successfully"}
    except (CropTypeNotFoundError, BusinessRuleViolationError, ResourceOwnershipError) as e:
        raise HTTPException(status_code=400, detail=str(e))