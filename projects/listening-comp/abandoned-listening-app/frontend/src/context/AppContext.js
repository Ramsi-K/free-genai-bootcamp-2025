import React, { createContext, useReducer, useContext } from 'react';

const initialState = {
  loading: false,
  error: null,
  // Video state
  currentVideo: null,
  videoList: [],
  // Practice session state
  session: {
    videoId: null,
    difficulty: 'intermediate',
    questions: [],
    currentQuestionIndex: 0,
    answers: [],
    score: 0,
    completed: false,
    audioPlaying: false
  },
  notification: null  // { type: 'success' | 'error' | 'info', message: string, duration?: number }
};

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_VIDEO_LIST':
      return { ...state, videoList: action.payload };
    case 'SET_CURRENT_VIDEO':
      return { ...state, currentVideo: action.payload };
    case 'START_PRACTICE_SESSION':
      return {
        ...state,
        session: {
          ...initialState.session,
          videoId: action.payload.videoId,
          difficulty: action.payload.difficulty,
          questions: action.payload.questions
        }
      };
    case 'SUBMIT_ANSWER':
      const { answer, isCorrect } = action.payload;
      return {
        ...state,
        session: {
          ...state.session,
          answers: [...state.session.answers, answer],
          score: isCorrect ? state.session.score + 1 : state.session.score,
          currentQuestionIndex: state.session.currentQuestionIndex + 1,
          completed: state.session.currentQuestionIndex + 1 >= state.session.questions.length
        }
      };
    case 'SET_AUDIO_PLAYING':
      return {
        ...state,
        session: {
          ...state.session,
          audioPlaying: action.payload
        }
      };
    case 'RESET_SESSION':
      return {
        ...state,
        session: initialState.session
      };
    case 'SET_NOTIFICATION':
      return {
        ...state,
        notification: action.payload
      };
    case 'CLEAR_NOTIFICATION':
      return {
        ...state,
        notification: null
      };
    default:
      return state;
  }
}

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Helper functions for common actions
  const showNotification = (message, type = 'info', duration = 3000) => {
    dispatch({
      type: 'SET_NOTIFICATION',
      payload: { message, type, duration }
    });
  };

  const contextValue = {
    state,
    dispatch,
    actions: {
      startLoading: () => dispatch({ type: 'SET_LOADING', payload: true }),
      stopLoading: () => dispatch({ type: 'SET_LOADING', payload: false }),
      setError: (error) => dispatch({ type: 'SET_ERROR', payload: error }),
      clearError: () => dispatch({ type: 'SET_ERROR', payload: null }),
      startPractice: (videoId, difficulty, questions) => 
        dispatch({ 
          type: 'START_PRACTICE_SESSION', 
          payload: { videoId, difficulty, questions } 
        }),
      submitAnswer: (answer, isCorrect) => 
        dispatch({ 
          type: 'SUBMIT_ANSWER', 
          payload: { answer, isCorrect } 
        }),
      resetSession: () => dispatch({ type: 'RESET_SESSION' }),
      setAudioPlaying: (playing) => 
        dispatch({ type: 'SET_AUDIO_PLAYING', payload: playing }),
      showNotification,
      clearNotification: () => dispatch({ type: 'CLEAR_NOTIFICATION' }),
      showSuccess: (msg) => showNotification(msg, 'success'),
      showError: (msg) => showNotification(msg, 'error', 5000),
      showInfo: (msg) => showNotification(msg, 'info')
    }
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}