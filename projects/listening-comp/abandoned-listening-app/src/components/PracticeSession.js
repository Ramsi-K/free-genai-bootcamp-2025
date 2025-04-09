import React, { useState, useEffect } from 'react';
import { loadQuestions, actions } from './actions';

const PracticeSession = () => {
    const [feedback] = useState(null);

    useEffect(() => {
        actions();
        loadQuestions();
    }, [actions, loadQuestions]);

    return (
        <div>
            {/* Render your component */}
        </div>
    );
};

export default PracticeSession;