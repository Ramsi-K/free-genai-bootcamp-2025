class ReviewBorder {
	constructor(scene,word) {
		this.scene = scene
		this.word = word
		this.graphics = this.scene.add.graphics();

		this.width = 256;
		this.height = 80;
	}

	update(){
		const spacing = 20
		this.y = this.word.y
		this.x = this.word.x

		this.graphics.clear();
		if (this.word.reviewed === true)
			this.graphics.lineStyle(1,0x00ff00, 1);
		else if (this.scene.marker_pos === this.word.index) {
			this.graphics.lineStyle(1,0xffffff, 1);
	 	} else {
			this.graphics.lineStyle(1,0x696969, 1);
		}
		this.graphics.strokeRect(
			this.x,
			this.y,
			this.width,
			this.height
		)
	}
}