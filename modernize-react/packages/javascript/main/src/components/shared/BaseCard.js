import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { Card, CardHeader, CardContent, Divider } from '@mui/material';
import { CustomizerContext } from 'src/context/CustomizerContext';


const BaseCard = ({ title, children }) => {
  const { isCardShadow } = useContext(CustomizerContext);

  return (
    <Card
      sx={{ padding: 0 }}
      elevation={isCardShadow ? 9 : 0}
      variant={!isCardShadow ? 'outlined' : undefined}
    >
      <CardHeader title={title} />
      <Divider />
      <CardContent>{children}</CardContent>
    </Card>
  );
};

BaseCard.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node,
};

export default BaseCard;
