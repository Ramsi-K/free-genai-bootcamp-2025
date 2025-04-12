from crewai import Crew
from crew import KoreanTutoringCrew

def main():
    # Initialize the Korean tutoring crew
    crew = KoreanTutoringCrew()
    
    # Start the crew's functionality
    crew.crew().kickoff()

if __name__ == "__main__":
    main()