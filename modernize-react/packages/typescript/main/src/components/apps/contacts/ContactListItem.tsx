/* eslint-disable @typescript-eslint/no-unused-vars */
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext } from 'react';


import {
  ListItemText,
  Box,
  Avatar,
  ListItemButton,
  Typography,
  Stack,
  ListItemAvatar,
  useTheme,
} from '@mui/material';

import { IconStar, IconTrash } from '@tabler/icons-react';
import { CustomizerContext } from 'src/context/CustomizerContext';

type Props = {
  onContactClick: (event: React.MouseEvent<HTMLElement>) => void;
  onStarredClick: React.MouseEventHandler<SVGElement>;
  onDeleteClick: React.MouseEventHandler<SVGElement>;
  id: string | number;
  firstname: string;
  lastname: string;
  image: string;
  department: string;
  starred: boolean;
  active: any;
};

const ContactListItem = ({
  onContactClick,
  onStarredClick,
  onDeleteClick,
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  id,
  firstname,
  lastname,
  image,
  department,
  starred,
  active,
}: Props) => {

  const { isBorderRadius } = useContext(CustomizerContext);

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const br = `${isBorderRadius}px`;

  const theme = useTheme();

  const warningColor = theme.palette.warning.main;

  return (
    <ListItemButton sx={{ mb: 1 }} selected={active} onClick={onContactClick}>
      <ListItemAvatar>
        <Avatar alt={image} src={image} />
      </ListItemAvatar>
      <ListItemText>
        <Stack direction="row" gap="10px" alignItems="center">
          <Box mr="auto" onClick={onContactClick}>
            <Typography variant="subtitle1" noWrap fontWeight={600} sx={{ maxWidth: '150px' }}>
              {firstname} {lastname}
            </Typography>
            <Typography variant="body2" color="text.secondary" noWrap>
              {department}
            </Typography>
          </Box>
          <IconStar
            onClick={(e) => {
              e.stopPropagation();
              onStarredClick(e);
            }}
            size="16"
            stroke={1.5}
            style={{ fill: starred ? warningColor : '', stroke: starred ? warningColor : '' }}
          />
          <IconTrash onClick={(e) => {
            e.stopPropagation();
            onDeleteClick(e);
          }} size="16" stroke={1.5} />
        </Stack>
      </ListItemText>
    </ListItemButton>
  );
};


export default ContactListItem;