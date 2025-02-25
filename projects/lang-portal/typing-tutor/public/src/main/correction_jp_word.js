class CorrectionJpWord {
	constructor(scene) {
		this.scene = scene
		this.size_en = 16
		this.size_kj = 48
		this.size_rj = 12

		const style_english = {
			font: `${this.size_en}px Arial`, 
			fill: '#ffffff'
		}
    const x_en = this.scene.game.config.width / 2
		this.txt_english = scene.add.text(x_en,0,'',style_english)
		this.txt_english.setOrigin(0.5,0);
		this.txt_english.visible = false

		// we can support words 8 kana long
		this.blocks = [
			new CorrectionJpWordBlock(scene,this,0),
			new CorrectionJpWordBlock(scene,this,1),
			new CorrectionJpWordBlock(scene,this,2),
			new CorrectionJpWordBlock(scene,this,3),
			new CorrectionJpWordBlock(scene,this,4),
			new CorrectionJpWordBlock(scene,this,5),
			new CorrectionJpWordBlock(scene,this,6),
			new CorrectionJpWordBlock(scene,this,7)
		]
	}

	set(word,d_index){
		this.d_index = d_index
		this.kanji = word.kanji
		this.romaji = word.romaji
		this.english = word.english
		this.kanji_len = word.kanji.length
		this.txt_english.visible = true

    const half_word_len = (this.kanji_len*this.size_kj) / 2
    const half_box_len =  this.scene.correction_box.width / 2
    const box_x = this.scene.correction_box.x
    const box_y = this.scene.correction_box.y
    const box_h = this.scene.correction_box.height
		this.x = box_x + half_box_len - half_word_len
		this.y = box_y + 24

    this.txt_english.setText(this.english)
		//this.txt_english.x = this.x + 8
		this.txt_english.y = box_y + box_h - 64

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
		this.blocks.forEach((block, index) => {
			block.update()
		})
	}

	remove(){
		this.d_index = null
		this.kanji = null
		this.romaji = null
		this.kanji_len = null
		this.txt_english.visible = false
		this.y = -this.size_kj
		this.blocks.forEach((block, index) => {
			block.remove()
		});
	}
}