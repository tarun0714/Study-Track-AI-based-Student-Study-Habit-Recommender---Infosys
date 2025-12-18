
import sys
import os

sys.path.append(os.getcwd())

from app.recommender import generate_recommendations

def test():
    # Test case: High study, low distraction, high score -> Should be "High Achiever"
    print("Testing High Achiever inputs:")
    try:
        res = generate_recommendations(study_hour=5.0, distraction_time=5.0, quiz_score=95.0)
        print(res)
    except Exception as e:
        print(f"Error: {e}")

    print("-" * 20)

    # Test case: Low study, high distraction, low score -> Should be "Needs Focus"
    print("Testing Needs Focus inputs:")
    try:
        res = generate_recommendations(study_hour=1.0, distraction_time=60.0, quiz_score=40.0)
        print(res)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
