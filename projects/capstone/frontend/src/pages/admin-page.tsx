import React, { useState } from 'react';
import { Shield, Trash2, RefreshCw, Database, CloudOff, Download, Upload, Settings, AlertTriangle } from 'lucide-react';

type ConfirmationModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  actionText: string;
  type: 'danger' | 'warning';
};

// Confirmation Modal Component
const ConfirmationModal = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  message, 
  actionText, 
  type 
}: ConfirmationModalProps) => {
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose}></div>
      <div className="glassmorphism rounded-lg p-6 w-full max-w-md relative animate-glow">
        <div className="mb-6 flex items-center">
          <div className={`p-3 rounded-full ${type === 'danger' ? 'bg-red-500/20' : 'bg-yellow-500/20'} mr-3`}>
            <AlertTriangle className={`h-6 w-6 ${type === 'danger' ? 'text-red-500' : 'text-yellow-500'}`} />
          </div>
          <h2 className="text-xl font-bold">{title}</h2>
        </div>
        
        <p className="mb-6 text-foreground/80">{message}</p>
        
        <div className="flex justify-end space-x-4">
          <button 
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-accent/50 hover:bg-accent/70 transition-colors"
          >
            Cancel
          </button>
          <button 
            onClick={onConfirm}
            className={`px-4 py-2 rounded-lg ${
              type === 'danger' 
                ? 'bg-red-500/80 hover:bg-red-500 text-white' 
                : 'bg-yellow-500/80 hover:bg-yellow-500 text-white'
            } transition-colors`}
          >
            {actionText}
          </button>
        </div>
      </div>
    </div>
  );
};

// Card component with hover effect
const AdminCard = ({ 
  title, 
  description, 
  icon, 
  buttonText,
  buttonType = 'primary',
  onClick
}: { 
  title: string;
  description: string;
  icon: React.ReactNode;
  buttonText: string;
  buttonType?: 'primary' | 'danger' | 'warning';
  onClick: () => void;
}) => {
  const buttonColors = {
    primary: 'from-blue-500 to-purple-600 hover:shadow-blue-500/20',
    danger: 'from-red-500 to-red-600 hover:shadow-red-500/20',
    warning: 'from-yellow-500 to-orange-500 hover:shadow-yellow-500/20'
  };

  return (
    <div className="glassmorphism rounded-lg p-6 border border-white/10 transition-all duration-300 hover:border-white/20">
      <div className="flex items-start">
        <div className="p-3 rounded-full bg-accent/20 mr-4 flex-shrink-0">
          {icon}
        </div>
        <div>
          <h3 className="text-lg font-semibold mb-2">{title}</h3>
          <p className="text-sm text-foreground/60 mb-4">{description}</p>
          <button
            onClick={onClick}
            className={`px-4 py-2 rounded-lg text-white bg-gradient-to-r ${buttonColors[buttonType]} hover:shadow-lg transition-all`}
          >
            {buttonText}
          </button>
        </div>
      </div>
    </div>
  );
};

// System Stats Card
const StatsCard = ({ title, value, icon }: { title: string; value: string; icon: React.ReactNode }) => {
  return (
    <div className="glassmorphism rounded-lg p-4 border border-white/10">
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-full bg-accent/20">
          {icon}
        </div>
        <div>
          <p className="text-sm text-foreground/60">{title}</p>
          <p className="text-lg font-semibold">{value}</p>
        </div>
      </div>
    </div>
  );
};

export default function AdminPage() {
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [showFullResetModal, setShowFullResetModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Mock stats data
  const stats = {
    totalWords: '2,450',
    studySessions: '87',
    lastBackup: '2 days ago',
    databaseSize: '256 MB'
  };
  
  const handleResetHistory = () => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setShowHistoryModal(false);
      setSuccessMessage('Study history has been reset successfully');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    }, 1500);
  };
  
  const handleFullReset = () => {
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setShowFullResetModal(false);
      setSuccessMessage('Application and database have been fully reset');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    }, 2000);
  };

  return (
    <div className="space-y-8 pt-20">
      {/* Header */}
      <div className="glassmorphism rounded-lg p-6">
        <div className="flex items-center space-x-4">
          <Shield className="h-8 w-8 text-blue-500" />
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        </div>
        <p className="mt-2 text-foreground/60">System management and database controls</p>
      </div>

      {/* Success message */}
      {successMessage && (
        <div className="glassmorphism rounded-lg p-4 border border-green-500/30 bg-green-500/10 animate-pulse">
          <p className="text-green-400">{successMessage}</p>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Words"
          value={stats.totalWords}
          icon={<Database className="h-5 w-5 text-blue-500" />}
        />
        <StatsCard
          title="Study Sessions"
          value={stats.studySessions}
          icon={<RefreshCw className="h-5 w-5 text-purple-500" />}
        />
        <StatsCard
          title="Last Backup"
          value={stats.lastBackup}
          icon={<CloudOff className="h-5 w-5 text-yellow-500" />}
        />
        <StatsCard
          title="Database Size"
          value={stats.databaseSize}
          icon={<Database className="h-5 w-5 text-green-500" />}
        />
      </div>

      {/* Admin Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AdminCard
          title="Reset Study History"
          description="This will clear all study history records while preserving user data and word collections."
          icon={<Trash2 className="h-6 w-6 text-yellow-500" />}
          buttonText="Reset History"
          buttonType="warning"
          onClick={() => setShowHistoryModal(true)}
        />

        <AdminCard
          title="Full System Reset"
          description="This will reset the entire application and database to its initial state. All user data will be lost."
          icon={<Trash2 className="h-6 w-6 text-red-500" />}
          buttonText="Full Reset"
          buttonType="danger"
          onClick={() => setShowFullResetModal(true)}
        />

        <AdminCard
          title="Export Database"
          description="Download a backup of the current database including all user data and word collections."
          icon={<Download className="h-6 w-6 text-blue-500" />}
          buttonText="Export Data"
          onClick={() => {
            // Implement database export functionality
            alert('Database export initiated');
          }}
        />

        <AdminCard
          title="Import Database"
          description="Restore the system from a previous backup file."
          icon={<Upload className="h-6 w-6 text-purple-500" />}
          buttonText="Import Data"
          onClick={() => {
            // Implement database import functionality
            alert('Database import would go here');
          }}
        />
      </div>

      {/* Advanced Settings */}
      <div className="glassmorphism rounded-lg p-6">
        <div className="flex items-center space-x-4 mb-6">
          <Settings className="h-6 w-6 text-blue-500" />
          <h2 className="text-xl font-bold">Advanced Settings</h2>
        </div>
        
        <div className="space-y-4">
          <div className="flex justify-between items-center border-b border-white/10 pb-4">
            <div>
              <h3 className="font-medium">Vector Database Integration</h3>
              <p className="text-sm text-foreground/60">Connect to external vector database for semantic search</p>
            </div>
            <div className="relative">
              <input 
                type="checkbox" 
                id="vector-db" 
                className="sr-only peer"
                defaultChecked 
              />
              <label 
                htmlFor="vector-db"
                className="block w-14 h-7 bg-accent/30 rounded-full cursor-pointer
                          peer-checked:bg-blue-500/50 after:content-[''] after:absolute 
                          after:top-1 after:left-1 after:bg-white after:rounded-full
                          after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-7"
              ></label>
            </div>
          </div>
          
          <div className="flex justify-between items-center border-b border-white/10 pb-4">
            <div>
              <h3 className="font-medium">OPEA Integration</h3>
              <p className="text-sm text-foreground/60">Connect to OPEA megaservices</p>
            </div>
            <div className="relative">
              <input 
                type="checkbox" 
                id="opea-integration" 
                className="sr-only peer"
                defaultChecked 
              />
              <label 
                htmlFor="opea-integration"
                className="block w-14 h-7 bg-accent/30 rounded-full cursor-pointer
                          peer-checked:bg-blue-500/50 after:content-[''] after:absolute 
                          after:top-1 after:left-1 after:bg-white after:rounded-full
                          after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-7"
              ></label>
            </div>
          </div>
          
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-medium">Debug Mode</h3>
              <p className="text-sm text-foreground/60">Enable detailed logging for troubleshooting</p>
            </div>
            <div className="relative">
              <input 
                type="checkbox" 
                id="debug-mode" 
                className="sr-only peer" 
              />
              <label 
                htmlFor="debug-mode"
                className="block w-14 h-7 bg-accent/30 rounded-full cursor-pointer
                          peer-checked:bg-blue-500/50 after:content-[''] after:absolute 
                          after:top-1 after:left-1 after:bg-white after:rounded-full
                          after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-7"
              ></label>
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Modals */}
      <ConfirmationModal
        isOpen={showHistoryModal}
        onClose={() => setShowHistoryModal(false)}
        onConfirm={handleResetHistory}
        title="Reset Study History"
        message="Are you sure you want to reset all study history? This action cannot be undone."
        actionText="Reset History"
        type="warning"
      />
      
      <ConfirmationModal
        isOpen={showFullResetModal}
        onClose={() => setShowFullResetModal(false)}
        onConfirm={handleFullReset}
        title="Full System Reset"
        message="WARNING: This will reset the entire application and database. All user data, progress, and word collections will be permanently deleted. This action cannot be undone."
        actionText="Confirm Full Reset"
        type="danger"
      />

      {/* Loading overlay */}
      {isLoading && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/50 backdrop-blur-sm">
          <div className="p-4 rounded-lg glassmorphism">
            <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mb-4 mx-auto"></div>
            <p className="text-center">Processing...</p>
          </div>
        </div>
      )}
    </div>
  );
}