import React, { useState, useEffect } from 'react';
import { Group } from '../types/api';
import { api } from '../lib/api';

interface GroupSelectorProps {
  onSelect: (groupId: number) => void;
}

export const GroupSelector: React.FC<GroupSelectorProps> = ({ onSelect }) => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [groupType, setGroupType] = useState<'pos' | 'theme'>('theme');

  useEffect(() => {
    api.getGroups(groupType).then(setGroups);
  }, [groupType]);

  return (
    <div className="space-y-4">
      <div className="flex gap-4">
        <button
          className={`btn-futuristic ${groupType === 'theme' ? 'neon-glow' : ''}`}
          onClick={() => setGroupType('theme')}
        >
          Theme Groups
        </button>
        <button
          className={`btn-futuristic ${groupType === 'pos' ? 'neon-glow' : ''}`}
          onClick={() => setGroupType('pos')}
        >
          Parts of Speech
        </button>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {groups.map(group => (
          <button
            key={group.id}
            onClick={() => onSelect(group.id)}
            className="hud-element hover-glow"
          >
            <h3 className="text-lg font-bold">{group.name}</h3>
            <p className="text-sm opacity-70">{group.words_count} words</p>
          </button>
        ))}
      </div>
    </div>
  );
};
