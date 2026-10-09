import os
import json
import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.database import engine, Base, get_db, SessionLocal
from app.models import Student, Submission
from app.pipeline.analyser import analyze_student_submission, AnalysisResult

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coding Misconception Detector Backend")

class SubmissionRequest(BaseModel):
    student_id: str
    student_name: str
    code: str

# Populate database with sample data if empty
@app.on_event("startup")
def startup_populate():
    db = SessionLocal()
    try:
        if db.query(Submission).count() == 0:
            sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_submissions.json')
            if os.path.exists(sample_path):
                with open(sample_path, 'r', encoding='utf-8') as f:
                    samples = json.load(f)
                
                for s in samples:
                    # Insert student if not exists
                    student = db.query(Student).filter(Student.id == s["student_id"]).first()
                    if not student:
                        student = Student(id=s["student_id"], name=s["student_name"])
                        db.add(student)
                    
                    # Insert submission
                    sub = Submission(
                        student_id=s["student_id"],
                        student_name=s["student_name"],
                        code=s["code"],
                        error_trace=s["error_trace"],
                        misconception_id=s["misconception_id"],
                        misconception_name=s["misconception_name"],
                        confidence=s["confidence"],
                        explanation=s["explanation"],
                        exercise=s["exercise"],
                        timestamp=datetime.datetime.fromisoformat(s["timestamp"])
                    )
                    db.add(sub)
                db.commit()
                print("Populated database with sample student submissions.")
            else:
                print(f"Sample data file not found at {sample_path}. Skipping initialization.")
    except Exception as e:
        db.rollback()
        print(f"Error initializing sample database content: {str(e)}")
    finally:
        db.close()

@app.post("/submit", response_model=AnalysisResult)
def submit_code(req: SubmissionRequest, db: Session = Depends(get_db)):
    """
    Submits student code for analysis. Runs the pipeline,
    records the student profile and the result, and returns analysis metrics.
    """
    if not req.student_id.strip() or not req.student_name.strip():
        raise HTTPException(status_code=400, detail="Student ID and Name must not be blank.")
        
    try:
        # Run pipeline
        result = analyze_student_submission(req.code)

        # Upsert student
        student = db.query(Student).filter(Student.id == req.student_id).first()
        if not student:
            student = Student(id=req.student_id, name=req.student_name)
            db.add(student)
        else:
            if student.name != req.student_name:
                student.name = req.student_name
                db.add(student)

        # Insert submission
        sub = Submission(
            student_id=req.student_id,
            student_name=req.student_name,
            code=req.code,
            error_trace=result.error_trace,
            misconception_id=result.misconception_id,
            misconception_name=result.misconception_name,
            confidence=result.confidence,
            explanation=result.explanation,
            exercise=result.micro_exercise
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process submission: {str(e)}")

@app.get("/history/{student_id}")
def get_history(student_id: str, db: Session = Depends(get_db)):
    """Returns the last 10 submissions for a specific student."""
    submissions = db.query(Submission)\
        .filter(Submission.student_id == student_id)\
        .order_by(Submission.timestamp.desc())\
        .limit(10)\
        .all()
    return submissions

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Returns aggregated misconception counts across all submissions."""
    results = db.query(
        Submission.misconception_name,
        func.count(Submission.id).label("count")
    ).filter(Submission.misconception_name != None)\
     .group_by(Submission.misconception_name)\
     .all()
    
    return {r.misconception_name: r.count for r in results if r.misconception_name}

@app.get("/top-misconceptions")
def get_top_misconceptions(db: Session = Depends(get_db)):
    """Returns the top 5 most frequent misconceptions."""
    results = db.query(
        Submission.misconception_name,
        func.count(Submission.id).label("count")
    ).filter(Submission.misconception_name != None)\
     .group_by(Submission.misconception_name)\
     .order_by(func.count(Submission.id).desc())\
     .limit(5)\
     .all()
     
    return [{"name": r.misconception_name, "count": r.count} for r in results]

@app.get("/students-summary")
def get_students_summary(db: Session = Depends(get_db)):
    """Returns all students with submission counts and their most common misconception."""
    students = db.query(Student).all()
    summary = []
    for s in students:
        subs = db.query(Submission).filter(Submission.student_id == s.id).all()
        counts = {}
        for sub in subs:
            if sub.misconception_name:
                counts[sub.misconception_name] = counts.get(sub.misconception_name, 0) + 1
        
        most_common = max(counts, key=counts.get) if counts else "None"
        summary.append({
            "student_id": s.id,
            "student_name": s.name,
            "submission_count": len(subs),
            "most_common_misconception": most_common
        })
    return summary

@app.get("/instructor-metrics")
def get_instructor_metrics(db: Session = Depends(get_db)):
    """Returns key dashboard metrics for the class."""
    total_submissions = db.query(Submission).count()
    unique_students = db.query(Student).count()
    
    # Calculate top misconception overall
    results = db.query(
        Submission.misconception_name,
        func.count(Submission.id).label("count")
    ).filter(Submission.misconception_name != None)\
     .group_by(Submission.misconception_name)\
     .order_by(func.count(Submission.id).desc())\
     .first()
     
    top_misconception = results.misconception_name if results else "None"
    
    return {
        "total_submissions": total_submissions,
        "unique_students": unique_students,
        "top_misconception": top_misconception
    }
