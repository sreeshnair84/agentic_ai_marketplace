'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { Project, type ProjectContext as ProjectContextType } from '@/types/project';
import { projectService } from '@/lib/projectApi';
import { useAuth } from './authContext';

interface ProjectAction {
  type: 'SET_PROJECTS' | 'SET_SELECTED_PROJECT' | 'SET_LOADING' | 'SET_ERROR' | 'ADD_PROJECT' | 'UPDATE_PROJECT' | 'DELETE_PROJECT';
  payload?: any;
}

const initialState: ProjectContextType = {
  selectedProject: null,
  projects: [],
  isLoading: false,
  error: null,
};

function projectReducer(state: ProjectContextType, action: ProjectAction): ProjectContextType {
  switch (action.type) {
    case 'SET_PROJECTS':
      return {
        ...state,
        projects: action.payload,
        isLoading: false,
      };
    case 'SET_SELECTED_PROJECT':
      return {
        ...state,
        selectedProject: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    case 'ADD_PROJECT':
      if (!action.payload) {
        console.error('ADD_PROJECT called with undefined payload');
        return state;
      }
      return {
        ...state,
        projects: [...state.projects, action.payload],
      };
    case 'UPDATE_PROJECT':
      if (!action.payload || !action.payload.id) {
        console.error('UPDATE_PROJECT called with invalid payload:', action.payload);
        return state;
      }
      return {
        ...state,
        projects: state.projects.map((p: Project) => 
          p.id === action.payload.id ? action.payload : p
        ),
        selectedProject: state.selectedProject?.id === action.payload.id 
          ? action.payload 
          : state.selectedProject,
      };
    case 'DELETE_PROJECT':
      return {
        ...state,
        projects: state.projects.filter((p: Project) => p.id !== action.payload),
        selectedProject: state.selectedProject?.id === action.payload 
          ? null 
          : state.selectedProject,
      };
    default:
      return state;
  }
}

const ProjectContext = createContext<{
  state: ProjectContextType;
  dispatch: React.Dispatch<ProjectAction>;
  selectProject: (project: Project | null) => void;
  createProject: (project: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
  updateProject: (id: string, updates: Partial<Project>) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  getFilteredProjects: (tags?: string[]) => Project[];
} | null>(null);

// No more mock data - projects must come from the API

export function ProjectProvider({ children }: { children: ReactNode }) {
  console.log('ProjectProvider component mounted');
  const [state, dispatch] = useReducer(projectReducer, initialState);
  const { state: authState } = useAuth();

  // Load projects when user is authenticated
  useEffect(() => {
    console.log('ProjectProvider useEffect triggered');
    console.log('Auth state:', authState);
    console.log('Is authenticated:', authState.isAuthenticated);
    console.log('Is loading auth:', authState.isLoading);
    
    // Only load projects if user is authenticated and auth is not loading
    if (!authState.isAuthenticated || authState.isLoading) {
      console.log('User not authenticated or auth still loading, skipping project load');
      return;
    }
    
    let isMounted = true; // Flag to prevent state updates if component unmounts
    
    const loadProjects = async () => {
      if (!isMounted) return;
      
      console.log('loadProjects function called for authenticated user');
      dispatch({ type: 'SET_LOADING', payload: true });
      
      try {
        console.log('Loading projects from API...');
        const projects = await projectService.getAll();
        
        if (!isMounted) return; // Don't update state if component unmounted
        
        console.log('Loaded projects:', projects);
        dispatch({ type: 'SET_PROJECTS', payload: projects });
        
        // Check for saved project in localStorage first
        const savedProjectId = localStorage.getItem('selectedProjectId');
        if (savedProjectId && projects.length > 0) {
          const savedProject = projects.find(p => p.id === savedProjectId);
          if (savedProject) {
            dispatch({ type: 'SET_SELECTED_PROJECT', payload: savedProject });
            return;
          }
        }
        
        // Set default project if none selected
        if (projects.length > 0) {
          try {
            const defaultProject = await projectService.getDefault();
            if (!isMounted) return;
            
            console.log('Default project:', defaultProject);
            dispatch({ type: 'SET_SELECTED_PROJECT', payload: defaultProject });
            localStorage.setItem('selectedProjectId', defaultProject.id);
          } catch (error) {
            if (!isMounted) return;
            
            // If no default project, find one marked as default or select the first one
            const defaultProject = projects.find(p => p.isDefault) || projects[0];
            console.log('Fallback to first/default project:', defaultProject);
            dispatch({ type: 'SET_SELECTED_PROJECT', payload: defaultProject });
            localStorage.setItem('selectedProjectId', defaultProject.id);
          }
        }
      } catch (error) {
        if (!isMounted) return;
        
        console.error('Failed to load projects:', error);
        dispatch({ type: 'SET_ERROR', payload: 'Failed to load projects' });
        dispatch({ type: 'SET_PROJECTS', payload: [] });
      }
    };

    loadProjects();
    
    // Cleanup function
    return () => {
      isMounted = false;
    };
  }, [authState.isAuthenticated, authState.isLoading]); // Depend on auth state

  // Clear projects when user logs out
  useEffect(() => {
    if (!authState.isAuthenticated && !authState.isLoading) {
      console.log('User logged out, clearing projects');
      dispatch({ type: 'SET_PROJECTS', payload: [] });
      dispatch({ type: 'SET_SELECTED_PROJECT', payload: null });
      localStorage.removeItem('selectedProjectId');
    }
  }, [authState.isAuthenticated, authState.isLoading]);

  const selectProject = (project: Project | null) => {
    dispatch({ type: 'SET_SELECTED_PROJECT', payload: project });
    // Save to localStorage for persistence
    if (project) {
      localStorage.setItem('selectedProjectId', project.id);
    } else {
      localStorage.removeItem('selectedProjectId');
    }
  };

  const createProject = async (projectData: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>) => {
    try {
      const newProject = await projectService.create(projectData);
      console.log('Created project:', newProject);
      
      if (!newProject || !newProject.id) {
        throw new Error('Invalid project returned from API');
      }
      
      dispatch({ type: 'ADD_PROJECT', payload: newProject });
    } catch (error) {
      console.error('Failed to create project:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to create project' });
    }
  };

  const updateProject = async (id: string, updates: Partial<Project>) => {
    try {
      const updatedProject = await projectService.update(id, updates);
      dispatch({ type: 'UPDATE_PROJECT', payload: updatedProject });
    } catch (error) {
      console.error('Failed to update project:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to update project' });
    }
  };

  const deleteProject = async (id: string) => {
    try {
      await projectService.delete(id);
      dispatch({ type: 'DELETE_PROJECT', payload: id });
    } catch (error) {
      console.error('Failed to delete project:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Failed to delete project' });
    }
  };

  const getFilteredProjects = (tags?: string[]) => {
    if (!tags || tags.length === 0) {
      return state.projects;
    }
    
    return state.projects.filter((project: Project) =>
      tags.some(tag => project.tags.includes(tag))
    );
  };

  return (
    <ProjectContext.Provider
      value={{
        state,
        dispatch,
        selectProject,
        createProject,
        updateProject,
        deleteProject,
        getFilteredProjects,
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
}

export const useProject = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
};
