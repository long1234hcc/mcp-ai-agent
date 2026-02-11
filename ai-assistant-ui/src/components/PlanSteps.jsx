import React from 'react';
import { FaCheckCircle, FaSpinner, FaCircle } from 'react-icons/fa';

const PlanSteps = ({ steps }) => {
  if (!steps || steps.length === 0) return null;

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <FaCheckCircle className="text-green-500" />;
      case 'in_progress':
        return <FaSpinner className="text-blue-500 animate-spin" />;
      default:
        return <FaCircle className="text-gray-300" />;
    }
  };

  return (
    <div className="bg-purple-50 rounded-lg p-4 mb-4">
      <h3 className="font-semibold text-purple-900 mb-3 flex items-center gap-2">
        <span>📋</span> Execution Plan
      </h3>
      <div className="space-y-2">
        {steps.map((step, index) => (
          <div key={index} className="flex items-start gap-3">
            <div className="mt-1">{getStatusIcon(step.status)}</div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-800">
                Step {step.id}: {step.description}
              </p>
              {step.result && (
                <p className="text-xs text-gray-600 mt-1 pl-3 border-l-2 border-purple-200">
                  {step.result.substring(0, 100)}...
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlanSteps;
