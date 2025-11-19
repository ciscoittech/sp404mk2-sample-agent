import { Card } from '@mui/material';
import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { CustomizerContext } from 'src/context/CustomizerContext';

const BlankCard = ({ children, className }) => {
  const { isCardShadow } = useContext(CustomizerContext);

  return (
    <Card
      sx={{ p: 0, position: 'relative' }}
      className={className}
      elevation={isCardShadow ? 9 : 0}
      variant={!isCardShadow ? 'outlined' : undefined}
    >
      {children}
    </Card>
  );
};

BlankCard.propTypes = {
  children: PropTypes.node,
};

export default BlankCard;
