"""Phase 2 — workshop job management: quotation -> mechanic approval -> assignment -> done."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/workshop", tags=["workshop — phase 2"])


@router.get("/jobs", response_model=list[schemas.RepairJobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(models.RepairJob).all()


@router.post("/jobs", response_model=schemas.RepairJobOut)
def create_job(payload: schemas.RepairJobCreate, db: Session = Depends(get_db)):
    job = models.RepairJob(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/{job_id}/approve", response_model=schemas.RepairJobOut)
def approve_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(models.RepairJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    job.status = models.JobStatus.approved
    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/{job_id}/assign", response_model=schemas.RepairJobOut)
def assign_mechanic(job_id: int, mechanic: str, db: Session = Depends(get_db)):
    job = db.get(models.RepairJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    job.mechanic = mechanic
    job.status = models.JobStatus.in_progress
    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/{job_id}/complete", response_model=schemas.RepairJobOut)
def complete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(models.RepairJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    job.status = models.JobStatus.done
    db.commit()
    db.refresh(job)
    return job
