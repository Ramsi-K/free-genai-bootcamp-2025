class PlayerData {
	constructor() {
		this.score = 0
		this.correct_words = []
		this.failed_words = []
	}

	add_correct_word(d_index) {
		this.correct_words.push(d_index)

	}

	add_failed_word(d_index) {
		this.failed_words.push(d_index)
	}

	async send_review(wordId, correct) {
		try {
			const apiUrl = `http://127.0.0.1:5000/study_sessions/${Data.study_session_id}/review`;  // Correct URL
			const response = await fetch(`${apiUrl}`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					word_id: wordId,
					correct: correct  // true for correct, false for wrong
				})
			});
	
			const data = await response.json();  // Handle the response
			console.log('Review submitted:', data);
		} catch (error) {
			console.error('Error sending review:', error);
		}
	}
}