import React, { useEffect } from 'react';

const VideoDetail = ({ videoId, loadVideoDetails }) => {
    useEffect(() => {
        loadVideoDetails();
    }, [loadVideoDetails]); // Added 'loadVideoDetails' to the dependency array

    return (
        <div>
            <h1>Video Details</h1>
            {/* Render video details here */}
        </div>
    );
};

export default VideoDetail;