from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.database import get_db
from schemas.chat import ConfirmationRequest
from schemas.response import ConfirmationResponse
from datetime import datetime
import json

router = APIRouter(prefix="/confirm", tags=["confirm"])

@router.post("/", response_model=ConfirmationResponse)
async def confirm_action(
    request: ConfirmationRequest,
    db: Session = Depends(get_db)
):
    """Confirm or reject a suggested action"""
    
    try:
        print(f"📋 Confirmation request - Decision: {request.decision}")
        print(f"🆔 File ID: {request.file_id}")
        print(f"🔗 Session ID: {request.session_id}")
        
        if request.decision.lower() not in ["yes", "no"]:
            raise HTTPException(
                status_code=400, 
                detail="Decision must be 'yes' or 'no'"
            )
        
        if request.decision.lower() == "yes":
            # Process the confirmed action
            results = {
                "action": "confirmed",
                "timestamp": datetime.now().isoformat(),
                "session_id": request.session_id,
                "file_id": request.file_id,
                "action_data": request.action_data
            }
            
            print(f"✅ Action confirmed and processed")
            
            return ConfirmationResponse(
                status="success",
                message="Action confirmed and executed successfully",
                results=results
            )
        else:
            # Action was rejected
            print(f"❌ Action rejected by user")
            
            return ConfirmationResponse(
                status="cancelled",
                message="Action was cancelled by user",
                results={
                    "action": "cancelled",
                    "timestamp": datetime.now().isoformat(),
                    "session_id": request.session_id
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Confirmation error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing confirmation: {str(e)}"
        ) 