class Missle {
	constructor(scene) {
		this.firing = false
		this.scene = scene
		this.speed = 5
		this.size = 8 // radius of circle
		this.circle = this.scene.add.circle(200, -9999, this.size, 0xff0000);
		this.reset_y_position()
	}

	reset_y_position(){
		this.y =  this.scene.game.config.height + this.size
		this.circle.y = this.y
	}

	update(){
		if (this.firing) {
			this.y -= this.speed
			this.circle.y = this.y
			if (this.y <= (this.word.y + this.word.size_kj)){
				this.hit()
			}
		}
	}

	// when the missle finally hit
	hit(){
		_player_data.add_correct_word(this.word.d_index)
		this.scene.word_manager.last_word = {
			d_index: this.word.d_index,
			status: 'correct'
		}
		this.word.targeted = false
		this.firing = false
		this.reset_y_position()
		this.scene.sound.play(this.word.romaji)
		_player_data.send_review(this.word.wordId,true)
		this.word.remove()
		this.scene.info_bar.add_score()
		this.check_blank_for_spawn()
	}

	// if there are no falling words spawn one immediately
	check_blank_for_spawn(){
		const all_not_falling = this.scene.word_manager.words.every(word => word.falling === false)
		if (all_not_falling){
			this.scene.timer.remove()
			this.scene.word_manager.spawn()
		}
	}

	fire(x,word){
		this.word = word
		this.word.targeted = true
		this.circle.x = x;
		this.firing = true
	}
}