class CorrectionBox {
  constructor(scene){
		this.scene = scene
		this.graphics = this.scene.add.graphics();
		this.x  = 432
		this.y  = 252
		this.width = 432
		this.height = 180
		this.userInput = '';

		this.word = new CorrectionJpWord(scene)

		const y_text = this.y + this.height - 22
		this.userText = this.scene.add.text(this.scene.game.config.width / 2, y_text, '', {
			font: '24px Arial',
			fill: '#ffffff'
		}).setOrigin(0.5);
		this.userText.visible = false
	}

	set(word){
		this.userInput = '';
		this.userText.setText(this.userInput)
		this.word.set(word)
		this.userText.visible = true
	}

	draw_box(){
		this.graphics.clear()
		this.graphics.fillStyle(0x000000)
		this.graphics.lineStyle(2, 0xFFFFFF)
		this.graphics.fillRect(
			this.x,
			this.y,
			this.width,
			this.height
		)
		this.graphics.strokeRect(
			this.x,
			this.y,
			this.width,
			this.height
		)

    this.graphics.beginPath();
    this.graphics.moveTo(432, 252+180-40);
    this.graphics.lineTo(432+432, 252+180-40);
    this.graphics.strokePath();
	}
	update(){
		this.word.highlight(this.userInput)
		this.word.update()
		this.draw_box()
	}

	input(ev){
		if (ev.key === 'Dead') {
			// Ignore the 'Dead' key event
			return;
		} else if (ev.key === 'Shift') {
			this.userInput = ''
		} else if (ev.keyCode === 8 && this.userInput.length > 0) {
			// Handle backspace
			this.userInput = this.userInput.slice(0, -1);
		} else if (ev.key === 'Enter') {
			this.correct()
			return;
		} else if ((ev.keyCode >= 65 && ev.keyCode <= 90) || ev.keyCode === 32) {
			// Add character for letters and space
			this.userInput += ev.key.toLowerCase();
		}
		this.userText.setText(this.userInput);
	}

	remove(){
		this.graphics.clear()
		this.userText.visible = false
	}

	correct(){
		if (this.word.valid(this.userInput)){
			this.scene.sound.play(this.word.english.replace(/ /g,'_'))
			this.scene.timer.paused = false
			this.scene.mode = 'falling'
			this.remove()
			this.word.remove()
		}
	}
}