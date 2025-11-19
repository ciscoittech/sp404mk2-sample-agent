import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { Card } from '@mui/material';
import { CustomizerContext } from 'src/context/CustomizerContext';


const AppCard = ({ children }) => {
  const { isCardShadow } = useContext(CustomizerContext);

  return (
    <Card
      sx={{ display: 'flex', p: 0 }}
      elevation={isCardShadow ? 9 : 0}
      variant={!isCardShadow ? 'outlined' : undefined}
    >
      {children}
    </Card>
  );
};

AppCard.propTypes = {
  children: PropTypes.node,
};

export default AppCard;
