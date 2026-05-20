from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from src.cultiva_lab.exceptions import (
    CropNotFoundError, CropTypeNotFoundError, UserNotFoundError,
    ResourceOwnershipError, InvalidInputError
)
from ..schemas.crop import CropResponse, CropCreateRequest, CropUpdateRequest, DailyConditionResponse, CropStatisticsResponse
from ..dependencies import get_current_user, get_crop_service, get_crop_type_service

router = APIRouter(prefix="/crops", tags=["Crops"])

@router.get("/", response_model=List[CropResponse])
def get_my_crops(
    current_user: dict = Depends(get_current_user),
    crop_service = Depends(get_crop_service)
):
    crops = crop_service.get_crops_by_user(current_user["id"], current_user["id"])
    return [CropResponse(id=c.id, name=c.name, crop_type_id=c.crop_type_id, start_date=c.start_date, last_sim_date=c.last_sim_date, active=c.active, water_stored=c.water_stored, consecutive_stress_days=c.consecutive_stress_days, current_phase=c.current_phase) for c in crops]

@router.get("/{crop_id}", response_model=CropResponse)
def get_crop_by_id(
    crop_id: str,
    current_user: dict = Depends(get_current_user),
    crop_service = Depends(get_crop_service)
):
    try:
        crop = crop_service.get_crop_by_id(crop_id, current_user["id"])
        return CropResponse(id=crop.id, name=crop.name, crop_type_id=crop.crop_type_id, start_date=crop.start_date, last_sim_date=crop.last_sim_date, active=crop.active, water_stored=crop.water_stored, consecutive_stress_days=crop.consecutive_stress_days, current_phase=crop.current_phase)
    except (CropNotFoundError, ResourceOwnershipError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
def create_crop(
    request: CropCreateRequest,
    current_user: dict = Depends(get_current_user),
    crop_service = Depends(get_crop_service)
):
    try:
        crop = crop_service.create_crop(
            name=request.name,
            crop_type_id=request.crop_type_id,
            water_stored=request.water_stored,
            user_id=current_user["id"],
            start_date=datetime.now()
        )
        return CropResponse(id=crop.id, name=crop.name, crop_type_id=crop.crop_type_id, start_date=crop.start_date, last_sim_date=crop.last_sim_date, active=crop.active, water_stored=crop.water_stored, consecutive_stress_days=crop.consecutive_stress_days, current_phase=crop.current_phase)
    except (UserNotFoundError, CropTypeNotFoundError, InvalidInputError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{crop_id}", response_model=CropResponse)
def update_crop(
    crop_id: str,
    request: CropUpdateRequest,
    current_user: dict = Depends(get_current_user),
    crop_service = Depends(get_crop_service)
):
    try:
        updates = {k: v for k, v in request.dict().items() if v is not None}
        updated = crop_service.update_crops(crop_id, current_user["id"], **updates)
        return CropResponse(id=updated.id, name=updated.name, crop_type_id=updated.crop_type_id, start_date=updated.start_date, last_sim_date=updated.last_sim_date, active=updated.active, water_stored=updated.water_stored, consecutive_stress_days=updated.consecutive_stress_days, current_phase=updated.current_phase)
    except (CropNotFoundError, ResourceOwnershipError, InvalidInputError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{crop_id}")
def delete_crop(
    crop_id: str,
    current_user: dict = Depends(get_current_user),
    crop_service = Depends(get_crop_service)
):
    try:
        crop_service.delete_crop(crop_id, current_user["id"])
        return {"message": "Crop deleted successfully"}
    except (CropNotFoundError, ResourceOwnershipError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{crop_id}/simulate", response_model=CropResponse)
def simulate_day(
    crop_id: str,
    temperature: float,
    rain: float,
    sun_hours: float,
    irrigation: float = 0.0,
    current_user: dict = Depends(get_current_user),
    crop_service = Depends(get_crop_service)
):
    try:
        updated = crop_service.simulate_day(crop_id, current_user["id"], temperature, rain, sun_hours, irrigation)
        return CropResponse(id=updated.id, name=updated.name, crop_type_id=updated.crop_type_id, start_date=updated.start_date, last_sim_date=updated.last_sim_date, active=updated.active, water_stored=updated.water_stored, consecutive_stress_days=updated.consecutive_stress_days, current_phase=updated.current_phase)
    except (CropNotFoundError, ResourceOwnershipError, InvalidInputError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{crop_id}/history", response_model=List[DailyConditionResponse])
def get_crop_history(
    crop_id: str,
    current_user: dict = Depends(get_current_user),
    crop_service = Depends(get_crop_service)
):
    try:
        history = crop_service.get_crop_history(crop_id, current_user["id"])
        return [DailyConditionResponse(day=h.day, temperature=h.temperature, rain=h.rain, sun_hours=h.sun_hours, estimated_biomass=h.estimated_biomass) for h in history]
    except (CropNotFoundError, ResourceOwnershipError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{crop_id}/stats", response_model=CropStatisticsResponse)
def get_crop_statistics(
    crop_id: str,
    current_user: dict = Depends(get_current_user),
    crop_service = Depends(get_crop_service)
):
    try:
        stats = crop_service.get_crop_statistics(crop_id, current_user["id"])
        return CropStatisticsResponse(**stats)
    except (CropNotFoundError, ResourceOwnershipError) as e:
        raise HTTPException(status_code=404, detail=str(e))