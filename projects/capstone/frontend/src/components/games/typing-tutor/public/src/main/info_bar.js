class InfoBar {
	constructor(scene) {
		this.scene = scene
		this.graphics = this.scene.add.graphics();
    this.width = this.scene.game.config.width
    this.height = 32
    this.x = 0
    this.y = this.scene.game.config.height - this.height
    this.add_words_text()
    this.add_score_text()
    this.add_groups_text()

    this.total_words = Data.words.length
    this.active_words = 0
  }

  add_groups_text(){
    const x = this.scene.game.config.width / 2
    const y = this.y + 4
    const text = Data.group_name
		this.groups_text = this.scene.add.text(x, y, text, {
			font: '20px Arial',
			fill: '#000000'
		}).setOrigin(0.5,0);
  }

  add_words_text(){
    const x = this.scene.game.config.width - 8
    const y = this.y + 4
    const text = `${this.active_words} / ${this.total_words} words`
		this.words_text = this.scene.add.text(x, y, text, {
			font: '20px Arial',
			fill: '#000000'
		}).setOrigin(1,0);
  }

  update_words_text(){
    this.active_words = this.scene.word_manager.active_words.length
    const text = `${this.active_words} / ${this.total_words} words`
    this.words_text.setText(text)
  }

  add_score_text(){
    const x = this.x + 8
    const y = this.y + 4
    const text = `${_player_data.score} pts`
		this.score_text = this.scene.add.text(x, y, text, {
			font: '20px Arial',
			fill: '#000000'
		}).setOrigin(0);
  }

	draw_box(){
		this.graphics.clear()
		this.graphics.fillStyle(0xCCCCCC)
		this.graphics.fillRect(
			this.x,
			this.y,
			this.width,
			this.height
		)
  }

	add_score(){
		_player_data.score += 10
		this.score_text.setText(`${_player_data.score} pts`);
	}

  update(){
    this.draw_box()
  }
}