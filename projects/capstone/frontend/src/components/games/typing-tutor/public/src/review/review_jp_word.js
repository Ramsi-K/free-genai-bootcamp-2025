class ReviewJpWord {
	constructor(scene,index) {
		this.index = index
		this.scene = scene
		this.size_en = 16
		this.size_kj = 32
		this.size_rj = 12

		const style_english = {
			font: `${this.size_en}px Arial`, 
			fill: '#ffffff'
		}
		this.txt_english = scene.add.text(0,0,'',style_english)
		this.txt_english.visible = true

		this.review_border = new ReviewBorder(scene,this)

		// we can support words 8 kana long
		this.blocks = [
			new ReviewJpWordBlock(scene,this,0),
			new ReviewJpWordBlock(scene,this,1),
			new ReviewJpWordBlock(scene,this,2),
			new ReviewJpWordBlock(scene,this,3),
			new ReviewJpWordBlock(scene,this,4),
			new ReviewJpWordBlock(scene,this,5),
			new ReviewJpWordBlock(scene,this,6),
			new ReviewJpWordBlock(scene,this,7)
		]
	}

	set(word,d_index, pos){
		this.d_index = d_index
		this.kanji = word.kanji
		this.romaji = word.romaji
		this.english = word.english
		this.kanji_len = word.kanji.length

		const row = Math.floor(this.index / 7)
		this.x = 48 + (row * 256) + (row * 16)
		
		const y_pos = this.index % 7
		const spacing = 40 + 16
		this.y = 48 + (y_pos*(this.size_kj+spacing))

    this.txt_english.setText(this.english)
		this.txt_english.x = this.x + 8
		this.txt_english.y = this.y + 80 - 24

		word.parts.forEach((part, index) => {
			this.blocks[index].set(
				this.x,
				this.y,
				part.kanji,
				part.romaji,
			)
		});
	}

	highlight(user_input) {
		let remaining_text = user_input
		this.blocks.forEach((block, index) => {
			remaining_text = block.highlight(remaining_text);
		});			
	}

	valid(user_input){
		return this.romaji === user_input
	}

	update(){
		this.review_border.update()
		this.blocks.forEach((block, index) => {
			block.update()
		})
	}
}