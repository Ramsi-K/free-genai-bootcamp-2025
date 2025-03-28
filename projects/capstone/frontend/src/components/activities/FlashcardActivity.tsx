import React from 'react';
import { GroupSelector } from '../GroupSelector';

const FlashcardActivity = () => {
  const handleGroupSelect = (groupId: number) => {
    // TODO: Start flashcard session with selected group
    console.log('Selected group:', groupId);
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold neon-text">Flashcards</h1>
      <p className="text-lg opacity-80">Select a word group to study:</p>
      <GroupSelector onSelect={handleGroupSelect} />
    </div>
  );
};

export default FlashcardActivity;
