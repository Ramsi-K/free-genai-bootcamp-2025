import React, { useEffect } from 'react';

const AudioPlayer = ({ handlePlay, handleEnded, handleError }) => {
    useEffect(() => {
        handlePlay();
    }, [handlePlay]); // Added 'handlePlay' to the dependency array

    useEffect(() => {
        handleEnded();
        handleError();
    }, [handleEnded, handleError]); // Added 'handleEnded' and 'handleError' to the dependency array

    return (
        <div>
            <audio controls>
                <source src="audio-file.mp3" type="audio/mpeg" />
                Your browser does not support the audio element.
            </audio>
        </div>
    );
};

export default AudioPlayer;