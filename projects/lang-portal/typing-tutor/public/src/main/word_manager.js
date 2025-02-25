class WordManager {
	constructor(scene) {
		this.scene = scene
		this.last_word = { status: '', d_index: null }
		this.active_words = []
		this.words = [
			new JpWord(this.scene),
			new JpWord(this.scene),
			new JpWord(this.scene),
			new JpWord(this.scene),
			new JpWord(this.scene),
			new JpWord(this.scene)
		];
	}

	// choose which word to drop next
	chooser(mode){
		let d_index = null;
		if (mode === 'random') {
			d_index = Phaser.Math.Between(0, Data.words.length-1)
		} else if (mode === 'progressive') {
			d_index = this.progressive_chooser()
		}
		this.scene.info_bar.update_words_text()
		return d_index;
	}

	progressive_chooser(initial_word_count = 5) {
    // === 1. Initialize Active Words ===
    if (this.active_words.length === 0) {
        const all_indices = Array.from({ length: Data.words.length }, (_, i) => i);
        for (let i = 0; i < initial_word_count && all_indices.length > 0; i++) {
            const random_index = Math.floor(Math.random() * all_indices.length);
            const chosen_index = all_indices.splice(random_index, 1)[0];
            this.active_words.push(chosen_index);
        }
        // Select and return a random word from active_words
        const initial_choice = this.active_words[Math.floor(Math.random() * this.active_words.length)];
        console.log(`Initial active_words: ${this.active_words}`);
        console.log(`Initial chosen word index: ${initial_choice}`);
        return initial_choice;
    }

    // === 2. Handle Last Word Failure ===
    if (this.last_word && this.last_word.status === 'failed') {
        console.log(`Last word failed. Repeating word index: ${this.last_word.d_index}`);
        return this.last_word.d_index;
    }

    // === 3. Build word_counts for All Active Words ===
    const word_counts = {};
    // Initialize counts to 0 for all active_words
    this.active_words.forEach(index => {
        word_counts[index] = 0;
    });
    // Increment counts based on _player_data.correct_words
    _player_data.correct_words.forEach(index => {
        if (word_counts.hasOwnProperty(index)) {
            word_counts[index] += 1;
        }
    });
    console.log(`Word counts: ${JSON.stringify(word_counts)}`);

    // === 4. Calculate Weighted Mastery Rate ===
    const masteryThreshold = 3;
    const requiredWeightedMasteryRate = 0.75; // 75%

    let masteredCount = 0;
    this.active_words.forEach(index => {
        if (word_counts[index] >= masteryThreshold) {
            masteredCount += 1;
        }
    });

    const weightedMasteryRate = masteredCount / this.active_words.length;
    console.log(`Mastered Count: ${masteredCount}`);
    console.log(`Weighted Mastery Rate: ${weightedMasteryRate}`);

    // === 5. Add New Word if Mastery Threshold is Met ===
    if (weightedMasteryRate >= requiredWeightedMasteryRate) {
        const inactive_indices = Data.words.map((_, i) => i).filter(index => !this.active_words.includes(index));
        
        if (inactive_indices.length > 0) {
            const random_index = Math.floor(Math.random() * inactive_indices.length);
            const chosen_index = inactive_indices[random_index];
            this.active_words.push(chosen_index);
            console.log(`Added new word at index ${chosen_index} to active_words.`);
            console.log(`Updated active_words: ${this.active_words}`);
            // Optionally, reset mastery counts or perform other actions here
        } else {
            console.warn("All words are already active. No new word to add.");
        }
    }

    // === 6. Calculate Weights for Selection ===
    // Weight calculation: Lower count => Higher weight
    // === Modification Start ===
    const weights = this.active_words.map(index => {
        // If the last word was correct, set its weight to 0 to exclude it
        if (this.last_word && this.last_word.status === 'correct' && index === this.last_word.d_index) {
            return 0;
        }
        return 1 / (1 + word_counts[index]);
    });
    // === Modification End ===
    console.log(`Weights: ${weights}`);

    // === 7. Calculate Cumulative Weights ===
    const cumulativeWeights = [];
    let totalWeight = 0;
    for (const weight of weights) {
        totalWeight += weight;
        cumulativeWeights.push(totalWeight);
    }
    console.log(`Cumulative Weights: ${cumulativeWeights}`);

    // === 8. Generate a Random Number for Selection ===
    const rand = Math.random() * totalWeight;
    console.log(`Random number for selection: ${rand}`);

    // === 9. Select the Word Based on Random Number ===
    let returned_word = this.active_words[this.active_words.length - 1]; // Default to last word
    for (let i = 0; i < cumulativeWeights.length; i++) {
        if (rand < cumulativeWeights[i]) {
            returned_word = this.active_words[i];
            break; // Exit loop once the word is found
        }
    }
    console.log(`Selected word index: ${returned_word}`);

    return returned_word;
	}

	spawn(){
		const d_index = this.chooser('progressive')
		const data = Data.words[d_index]

		const word = this.words.find(w => w.falling === false)
		if (word === undefined){
			// do nothing because none are avaliable
		} else {
			word.set(data, d_index)
		}
		
		// The longer the romaji the more time to get the word.
		const delay = (1000 * word.romaji.length) + 1000
		this.scene.addSpawnTimer(delay)
	}

	update(){
		this.words.forEach((word,index) => {
			word.update();
		})
		this.highlight()
	}

	highlight(){
		this.words.forEach((word,index) => {
			word.highlight(this.scene.userInput);
		})
	}
}