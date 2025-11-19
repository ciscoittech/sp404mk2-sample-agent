// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext } from 'react';

import { Card } from '@mui/material';

import { CustomizerContext } from 'src/context/CustomizerContext';

type Props = {
  children: any | any[]
};

const AppCard = ({ children }: Props) => {

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

export default AppCard;
