import { renderHook } from '@testing-library/react-hooks';
import { useLocalStorage } from '../../hooks/useLocalStorage';
import { useStudySession } from '../../hooks/useStudySession';
import { useVectorDB } from '../../hooks/useVectorDB';
import { useStudyStore } from '../../store/study';

describe('Utility Functions and Hooks', () => {
  test('useLocalStorage should initialize with default value', () => {
    const { result } = renderHook(() => useLocalStorage('testKey', 'defaultValue'));
    expect(result.current[0]).toBe('defaultValue');
  });

  test('useStudySession should track session time', () => {
    const { result } = renderHook(() => useStudySession('word'));
    expect(result.current.elapsedTime).toBe(0);
  });

  test('useVectorDB should return results from search', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useVectorDB());
    await result.current.search('test', 5);
    expect(result.current.results).toHaveLength(5);
  });

  test('useStudyStore should manage study session state', () => {
    const { result } = renderHook(() => useStudyStore());
    act(() => {
      result.current.startSession('word');
    });
    expect(result.current.activeSession).not.toBeNull();
  });
});