class JpWord {
	constructor(scene) {
		this.falling = false
		this.targeted = false
		this.scene = scene
		this.size_kj = 32
		this.size_rj = 12

		// we can support words 8 kana long
		this.blocks = [
			new JpWordBlock(scene,this,0),
			new JpWordBlock(scene,this,1),
			new JpWordBlock(scene,this,2),
			new JpWordBlock(scene,this,3),
			new JpWordBlock(scene,this,4),
			new JpWordBlock(scene,this,5),
			new JpWordBlock(scene,this,6),
			new JpWordBlock(scene,this,7)
		]
	}

	skyline_block_random_unhit_index() {
		// Create an array of indices where hit is false
		const unhitIndices = this.scene.skyline.reduce((indices, item, index) => {
			if (item.hit === false) {
				indices.push(index);
			}
			return indices;
		}, []);
		
		// If there are no unhit items, return -1
		if (unhitIndices.length === 0) {
			return -1;
		}
		
		// Generate a random index from the unhitIndices array
		const randomIndex = Math.floor(Math.random() * unhitIndices.length);
		
		// Return the randomly selected index from the original array
		return unhitIndices[randomIndex];
	}	

	set(word,d_index){
		this.wordId = word.id
		this.d_index = d_index
		this.kanji = word.kanji
		this.romaji = word.romaji
		this.kanji_len = word.kanji.length
		
		const unhit_index = this.skyline_block_random_unhit_index()

		if (unhit_index === -1){
			if (this.scene.skyline.every(item => item.hit === true)) {
				this.scene.scene.start('SceneReview')
			}
		}

		let offset
		// its 39 instead of 40 because we start at zero
		// we need to subtract 1 from kanji length because 0 will take up a single kanji
		if (unhit_index+(this.kanji_len-1) > 39){
			offset = (unhit_index+(this.kanji_len-1))-39
			this.pos = unhit_index-offset
		} else {
			this.pos = unhit_index
		}

		this.x = this.pos * 32
		
		// The idea is to change the speed based on the length of the word.
		// This is not working great since we end up with multiple words at the same time
		// so for now lets just fix the speed.
		// this.speed = 1.0 - (0.1 * Math.round(word.romaji.length / 2))
		this.speed = 0.4

		this.y = -this.size_kj // Phaser.Math.Between(0, scene.game.config.height)
		this.falling = true

		word.parts.forEach((part, index) => {
			this.blocks[index].set(
				this.x,
				this.y,
				part.kanji,
				part.romaji,
				this.size_kj,
				this.size_rj
			)
		});
	}

	highlight(user_input) {
		let remaining_text = user_input
		this.blocks.forEach((block, index) => {
			remaining_text = block.highlight(remaining_text);
		});			
	}

	update(){
		if (this.falling === false){
			return
		}
		const hitline = this.scene.game.config.height - 80
		if (this.y >= hitline) {
			this.hit()
		} else {
			this.y += this.speed
			this.blocks.forEach((block, index) => {
				block.update()
			})
		}
	}

	hit(){
		this.scene.word_manager.last_word = {
			d_index: this.d_index,
			status: 'failed'
		}
		this.scene.userInput = ''
		this.scene.userText.setText(this.userInput)
		this.scene.timer.paused = true
		this.scene.sound.play(this.romaji)
		this.scene.hit(this.kanji_len,this.pos)
		this.scene.mode = 'correction'
		this.scene.correction_box.set(Data.words[this.d_index],this.d_index)
		_player_data.add_failed_word(this.d_index)
		_player_data.send_review(this.wordId,false)
		this.remove()
	}

	x_middle(){
		const len = this.kanji_len * this.size_kj
		return this.x + (len/2)
	}

	valid_target(user_input){
		if (this.falling === false){
			return
		}
		return this.romaji === user_input
	}
	
	remove(){
		this.d_index = null
		this.falling = false
		this.kanji = null
		this.romaji = null
		this.kanji_len = null
		this.y = -this.size_kj
		this.blocks.forEach((block, index) => {
			block.remove()
		});
	}
}