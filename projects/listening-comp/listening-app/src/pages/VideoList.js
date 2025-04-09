import React, { useEffect } from 'react';
import VideoItem from './VideoItem';

const VideoList = ({ videos, fetchVideos }) => {
    useEffect(() => {
        fetchVideos();
    }, [fetchVideos]); // Added 'fetchVideos' to the dependency array

    return (
        <div>
            {videos.map((video) => (
                <VideoItem key={video.id} video={video} />
            ))}
        </div>
    );
};

export default VideoList;