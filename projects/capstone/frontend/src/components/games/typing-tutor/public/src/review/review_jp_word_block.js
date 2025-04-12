class ReviewJpWordBlock {
	constructor(scene,word,index) {
    this.reviewed = false
    this.activated = false
		this.scene = scene
		this.word = word
		this.index = index
		this.match_per = 0

		const style_kanji = {
			font: `${this.word.size_kj}px Arial`, 
			fill: '#ffffff',
			stroke: '#000000',
			strokeThickness:  8
		}

		const style_kanji_masked = {
			font: `${this.word.size_kj}px Arial`, 
			fill: '#00ff00',
			stroke: '#000000',
			strokeThickness:  8
		}

		const style_romaji = {font: `${this.word.size_rj}px Arial`, fill: '#ffffff'}

		this.kanji = scene.add.text(0,0,'',style_kanji)
		this.kanji.visible = false

		this.kanji_masked = scene.add.text(0,0,'',style_kanji_masked)
		this.kanji_masked.visible = false

		this.romaji = scene.add.text(0,0,'',style_romaji)
		this.romaji.visible = false

		// Create a rectangle to use as a mask
		this.maskShape = this.scene.make.graphics();
		this.mask = new Phaser.Display.Masks.GeometryMask(this.scene, this.maskShape);
  }

	set(x_offset,y_offset,txt_kanji,txt_romaji){
    this.activated = true
		this.txt_romaji = txt_romaji

		const block_offset = (this.index * this.word.size_kj)

		const x_kanji = block_offset + x_offset
		const y_kanji = 0 + y_offset + 16

		const x_romaji = block_offset + x_offset + 4
		const y_romaji = y_offset + 4

		this.kanji.setText(txt_kanji)
		this.kanji.x = x_kanji
		this.kanji.y = y_kanji
		this.kanji.visible = true

		this.kanji_masked.setText(txt_kanji)
		this.kanji_masked.x = x_kanji
		this.kanji_masked.y = y_kanji
		this.kanji_masked.visible = true

		this.romaji.setText(txt_romaji.join(''))
		this.romaji.x = x_romaji
		this.romaji.y = y_romaji
		this.romaji.visible = true
	}

	highlight(user_input) {
    if (this.activated === false) {
      return
    }
		if (user_input === false || user_input === undefined) {
			this.match_per = 0
			return
		}

		const txt_romaji_joined = this.txt_romaji.join('')
		if (user_input.startsWith(txt_romaji_joined)) {
			this.match_per = 1
			return user_input.slice(txt_romaji_joined.length);
		} else {
			// partial match
			const matched = this.sequentialMatch(this.txt_romaji,user_input)
			if (matched === 0) {
				// no match
				this.match_per = 0
				this.kanji.setColor('#ffffff'); // White
				return false;
			} else {
				// matched
				this.match_per = matched / this.txt_romaji.length
				this.update_mask()
				// it still false because its not a complete match
				return false;
			} // if
		}	// if			
	} // highlight

	sequentialMatch(arr, str) {
		let matchCount = 0;
		let currentIndex = 0;
	
		for (let part of arr) {
			if (str.startsWith(part, currentIndex)) {
				matchCount++;
				currentIndex += part.length;
			} else {
				break;
			}
		}
		return matchCount;
	}

	reset_highlight(){
		this.match_per = 0
	}

	update(){
		this.update_mask()
	}

	update_mask(){
		this.maskShape.clear()
		this.maskShape.fillStyle(0xffff00) // yellow mask
		// fillRect(x, y, width, height)
		const width = (this.word.size_kj + 8) * this.match_per
		// +8 due to border
		this.maskShape.fillRect(
			this.kanji_masked.x, 
			this.kanji_masked.y, 
			width,
			this.word.size_kj + 8
		);
		this.kanji_masked.setMask(this.mask);
	}
}