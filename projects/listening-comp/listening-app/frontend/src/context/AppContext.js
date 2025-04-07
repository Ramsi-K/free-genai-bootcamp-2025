import React, { createContext, useReducer, useContext } from 'react';

// Initial state
const initialState = {
  isLoading: false,
  error: null,
  questions: [],
  currentQuestionIndex: 0,
  userAnswers: [],
  correctAnswers: 0,
};

// Reducer function
function appReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_QUESTIONS':
      return { ...state, questions: action.payload, currentQuestionIndex: 0, userAnswers: [], correctAnswers: 0 };
    case 'ANSWER_QUESTION':
      const isCorrect = action.payload.isCorrect;
      return {
        ...state,
        userAnswers: [...state.userAnswers, action.payload.answer],
        correctAnswers: isCorrect ? state.correctAnswers + 1 : state.correctAnswers,
        currentQuestionIndex: state.currentQuestionIndex + 1,
      };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

// Create context
const AppContext = createContext();

// Context provider
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

// Custom hook to use the context
export function useAppContext() {
  return useContext(AppContext);
}