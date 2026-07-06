import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class MemoryService:
    """
    Firestore-backed Student Learning Memory Service.
    Tracks quiz scores, weak topics, revision history, and exam goals.
    Includes fallback mechanisms to run without active Firestore credentials.
    """
    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.db = None
        try:
            from google.cloud import firestore
            self.db = firestore.AsyncClient(project=self.project_id)
            logger.info("MemoryService: Async Firestore Client initialized successfully.")
        except Exception as e:
            logger.warning(f"MemoryService: Could not initialize Firestore Client: {e}. Using mock mode.")

    async def save_quiz_score(
        self,
        user_id: str,
        subject: str,
        score: int,
        max_score: int,
        topic: str
    ) -> str:
        """
        Saves student quiz attempts and scores to Firestore.
        """
        logger.info(f"MemoryService: Saving quiz score for user={user_id}, score={score}/{max_score}")
        data = {
            "user_id": user_id,
            "subject": subject,
            "score": score,
            "max_score": max_score,
            "topic": topic,
            "timestamp": firestore.SERVER_TIMESTAMP if self.db else "mock_timestamp"
        }
        if self.db:
            try:
                doc_ref = await self.db.collection("quiz_scores").add(data)
                return doc_ref[1].id
            except Exception as e:
                logger.error(f"Firestore save_quiz_score failed: {e}")
        return "mock_quiz_score_id"

    async def update_weak_topics(
        self,
        user_id: str,
        subject: str,
        weak_topics: List[str]
    ) -> None:
        """
        Updates student's cumulative weak topics list.
        """
        logger.info(f"MemoryService: Updating weak topics for user={user_id}, topics={weak_topics}")
        if self.db:
            try:
                doc_ref = self.db.collection("student_profiles").document(user_id)
                await doc_ref.set({
                    "weak_topics": {subject: weak_topics}
                }, merge=True)
            except Exception as e:
                logger.error(f"Firestore update_weak_topics failed: {e}")

    async def log_revision(
        self,
        user_id: str,
        subject: str,
        topic: str,
        details: str
    ) -> None:
        """
        Appends a revision milestone to student's history.
        """
        logger.info(f"MemoryService: Logging revision for user={user_id}, topic={topic}")
        data = {
            "user_id": user_id,
            "subject": subject,
            "topic": topic,
            "details": details,
            "timestamp": firestore.SERVER_TIMESTAMP if self.db else "mock_timestamp"
        }
        if self.db:
            try:
                await self.db.collection("revision_history").add(data)
            except Exception as e:
                logger.error(f"Firestore log_revision failed: {e}")

    async def set_exam_goal(
        self,
        user_id: str,
        exam: str,
        target_score: Optional[int] = None
    ) -> None:
        """
        Sets or updates target exam focus and goals.
        """
        logger.info(f"MemoryService: Setting exam goal for user={user_id}, exam={exam}")
        if self.db:
            try:
                doc_ref = self.db.collection("student_profiles").document(user_id)
                await doc_ref.set({
                    "exam_goal": exam,
                    "target_score": target_score
                }, merge=True)
            except Exception as e:
                logger.error(f"Firestore set_exam_goal failed: {e}")

    async def get_student_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves the consolidated learning profile progress for a student.
        """
        logger.info(f"MemoryService: Retrieving progress profile for user={user_id}")
        if self.db:
            try:
                profile_ref = self.db.collection("student_profiles").document(user_id)
                profile_doc = await profile_ref.get()
                profile_data = profile_doc.to_dict() or {}

                # Query quiz scores
                scores_ref = self.db.collection("quiz_scores").where("user_id", "==", user_id)
                scores_docs = await scores_ref.get()
                scores = [doc.to_dict() for doc in scores_docs]

                return {
                    "user_id": user_id,
                    "exam_goal": profile_data.get("exam_goal", "none"),
                    "target_score": profile_data.get("target_score"),
                    "weak_topics": profile_data.get("weak_topics", {}),
                    "quiz_scores": scores
                }
            except Exception as e:
                logger.error(f"Firestore get_student_progress failed: {e}")

        # Mock response when DB offline or fallback
        return {
            "user_id": user_id,
            "exam_goal": "neet",
            "target_score": 680,
            "weak_topics": {
                "physics": ["Coulomb's Law", "Ray Optics refraction"],
                "chemistry": ["Ionic Bonding"]
            },
            "quiz_scores": [
                {"subject": "physics", "score": 4, "max_score": 5, "topic": "Electric Charges"},
                {"subject": "chemistry", "score": 2, "max_score": 5, "topic": "Chemical Bonding"}
            ]
        }
