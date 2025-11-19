import { useNavigate } from 'react-router';
import useAuth from './UseAuth';
import { useEffect } from 'react';

const GuestGuard = ({ children }: any) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return children;
};

export default GuestGuard;
