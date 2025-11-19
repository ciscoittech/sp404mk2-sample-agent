import { useNavigate } from 'react-router';
import useAuth from './UseAuth';
import { useEffect } from 'react';

const AuthGuard = ({ children }: any) => {
  const { isAuthenticated } = useAuth();

  const navigate = useNavigate();

  useEffect(() => {

    if (!isAuthenticated) {
      navigate('/auth/login', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return children;
};

export default AuthGuard;
