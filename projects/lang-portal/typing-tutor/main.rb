require 'aws-sdk-polly'
require 'pry'
require 'json'
require 'fileutils'

class Text2Voice
 
  def self.client
    Aws::Polly::Client.new
  end

  # override existing files
  def self.run data_path:, output_path:, voiceid:, override: false

    json = File.read(data_path)
    data = JSON.parse json
    
    FileUtils.mkdir_p(output_path + '/jp')
    FileUtils.mkdir_p(output_path + '/en')

    data.each_with_index do |t,i|
      text = t['romaji']
      audio_path = File.join(output_path, 'jp', "#{text.gsub(/ /,'_')}.mp3")
      if override && File.exist?(audio_path)
        puts "Japanese file: #{audio_path} already exists. Skipping synthesis."
      else
        self.synth text: text, audio_path: audio_path, client: client, voiceid: voiceid[0]
      end

      text = t['english']
      audio_path = File.join(output_path, 'en', "#{text.gsub(/ /,'_')}.mp3")
      if override && File.exist?(audio_path)
        puts "English file: #{audio_path} already exists. Skipping synthesis."
      else
        self.synth text: text, audio_path: audio_path, client: client, voiceid: voiceid[1]
      end
    end # each_with_index
  end

  def self.synth text:, audio_path:, client:, voiceid:
    resp = client.synthesize_speech({
      engine: "neural",
      output_format: "mp3", 
      text: text,
      text_type: "text", 
      voice_id: voiceid, 
    })
    File.open(audio_path, 'w') do |file| 
      data = resp.audio_stream.read
      file.write data
    end
  end
end