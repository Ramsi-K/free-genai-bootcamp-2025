import os
import json
from datetime import datetime
from config import APP_CONFIG

# Progress file path
PROGRESS_FILE = os.path.join(APP_CONFIG.get("data_dir", "data"), "progress.json")

def update_progress(stats):
    """Update progress stats."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
        
        # Load existing progress
        progress = {
            "total_quizzes": 0,
            "total_questions": 0,
            "correct_answers": 0,
            "recent_quizzes": []
        }
        
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                progress = json.load(f)
        
        # Update overall stats
        progress["total_quizzes"] += 1
        progress["total_questions"] += stats.get("total_questions", 0)
        progress["correct_answers"] += stats.get("correct_answers", 0)
        
        # Create recent quiz entry
        quiz_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "difficulty": stats.get("difficulty", "medium"),
            "total_questions": stats.get("total_questions", 0),
            "correct_answers": stats.get("correct_answers", 0),
            "accuracy": stats.get("accuracy", 0)
        }
        
        # Add to recent quizzes, keep only the last 10
        progress["recent_quizzes"].append(quiz_entry)
        progress["recent_quizzes"] = progress["recent_quizzes"][-10:]
        
        # Save updated progress
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error updating progress: {e}")

def get_progress_stats():
    """Get progress statistics."""
    try:
        if not os.path.exists(PROGRESS_FILE):
            return None
            
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            progress = json.load(f)
            
        # Calculate overall accuracy
        overall_accuracy = 0
        if progress.get("total_questions", 0) > 0:
            overall_accuracy = round((progress.get("correct_answers", 0) / progress.get("total_questions", 1)) * 100)
            
        # Add overall accuracy to the progress data
        progress["overall_accuracy"] = overall_accuracy
        
        # Get vocabulary count if available
        try:
            from vocabulary import get_vocabulary_count
            progress["vocabulary_count"] = get_vocabulary_count()
        except ImportError:
            progress["vocabulary_count"] = 0
            
        return progress
        
    except Exception as e:
        print(f"Error getting progress stats: {e}")
        return None

def display_progress():
    """Display progress statistics."""
    try:
        progress = get_progress_stats()
        
        if not progress:
            print("\nNo progress data available yet.")
            return
            
        print("\n📊 Progress Statistics")
        print("-" * 50)
        print(f"Total Quizzes Completed: {progress.get('total_quizzes', 0)}")
        print(f"Total Questions Answered: {progress.get('total_questions', 0)}")
        print(f"Overall Accuracy: {progress.get('overall_accuracy', 0)}%")
        print(f"Vocabulary Words Collected: {progress.get('vocabulary_count', 0)}")
        
        # Provide encouraging feedback based on performance
        accuracy = progress.get("overall_accuracy", 0)
        if accuracy >= 90:
            print("\n🌟 Excellent work! Your listening comprehension is outstanding!")
        elif accuracy >= 70:
            print("\n👍 Great progress! Keep up the good work!")
        elif accuracy >= 50:
            print("\n💪 You're making steady progress. Keep practicing!")
        else:
            print("\n🌱 Every practice session helps you improve. Don't give up!")
        
        # Display recent quiz history
        recent_quizzes = progress.get("recent_quizzes", [])
        if recent_quizzes:
            print("\nRecent Quiz History:")
            print("-" * 50)
            for i, quiz in enumerate(reversed(recent_quizzes)):
                print(f"{i+1}. {quiz.get('timestamp')} - " 
                      f"Difficulty: {quiz.get('difficulty', 'unknown').capitalize()}, "
                      f"Score: {quiz.get('correct_answers', 0)}/{quiz.get('total_questions', 0)} "
                      f"({quiz.get('accuracy', 0)}%)")
                
    except Exception as e:
        print(f"Error displaying progress: {e}")
        
    input("\nPress Enter to continue...")

def display_final_score(score, total):
    """Display the final score for a quiz session with encouraging feedback."""
    print("\n===== Quiz Results =====")
    print(f"Your Score: {score}/{total}")
    
    # Calculate percentage
    if total > 0:
        percentage = (score / total) * 100
        print(f"Accuracy: {percentage:.1f}%")
        
        # Provide feedback based on performance
        if percentage >= 90:
            print("\n🌟 Excellent work! Your listening comprehension is outstanding!")
        elif percentage >= 80:
            print("\n😀 Great job! You're making excellent progress!")
        elif percentage >= 70:
            print("\n👍 Good progress! Keep up the good work!")
        elif percentage >= 50:
            print("\n💪 You're making steady progress. Keep practicing!")
        else:
            print("\n🌱 Every practice session helps you improve. Don't give up!")
    
    # Add a personal touch
    words_of_encouragement = [
        "Learning a language is a journey, not a destination.",
        "Consistency is key to language mastery!",
        "Your brain is forming new connections with every practice session.",
        "Korean fluency is getting closer with each quiz you take!",
        "Great work on challenging yourself today!"
    ]
    import random
    print(f"\n💭 {random.choice(words_of_encouragement)}")
    
    input("\nPress Enter to continue...")