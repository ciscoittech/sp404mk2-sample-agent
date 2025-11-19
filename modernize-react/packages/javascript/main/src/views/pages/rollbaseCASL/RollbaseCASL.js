import React from 'react';
import { defineAbility } from '@casl/ability';
import { Can } from '@casl/react';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import { Box, Button, List, ListItem, Stack } from '@mui/material';
import ParentCard from 'src/components/shared/ParentCard';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'CASL',
  },
];

const permissions = {
  CanEdit: {
    action: 'Can-edit',
    subject: 'address',
  },
  CanDelete: {
    action: 'Can-delete',
    subject: 'address',
  },
};

const users = {
  Admin: {
    permissions: ['CanEdit', 'CanDelete'],
  },
  Manager: {
    permissions: ['CanEdit'],
  },
  Subscriber: {
    permissions: [],
  },
};

const addresses = [
  {
    city: 'New York',
    street: '5684 Max Summit',
    type: 'address',
  },
  {
    city: 'Manhatten York',
    street: '5684 Max Summit',
    type: 'address',
  },
  {
    city: 'Canada street York',
    street: '5684 Max Summit',
    type: 'address',
  },
  {
    city: 'Delhi street',
    street: '5684 Max Summit',
    type: 'address',
  },
  {
    city: 'UP Chawk',
    street: '5684 Max Summit',
    type: 'address',
  },
];

const RollbaseCASL = () => {
  const [userId, setUserId] = React.useState(Object.keys(users)[0]);
  const userPermissions = users[userId].permissions.map((id) => permissions[id]);

  const actions = [
    ...userPermissions.reduce((collection, { action }) => {
      collection.add(action);
      return collection;
    }, new Set()),
  ];

  const ability = defineAbility((can) => {
    userPermissions.forEach(({ action, subject }) => {
      can(action, subject);
    });
  });

  return (
    <PageContainer title="Rollbase Access" description="this is Rollbase Access">
      {/* breadcrumb */}
      <Breadcrumb title="Pricing" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Permission Base Access with CASL">
        <Stack direction={'row'} gap={1}>
          {Object.entries(users).map(([id]) => (
            <Button
              key={id}
              variant={userId !== id ? 'outlined' : 'contained'}
              color="primary"
              onClick={() => setUserId(id)}
            >
              {id}
            </Button>
          ))}
        </Stack>
        <Box p={2} mt={2} bgcolor={'primary.light'}>
          {users[userId].permissions.map((permission) => (
            <Box key={permission}>{permission}</Box>
          ))}
        </Box>

        <List>
          {addresses.map(({ city, street, type }) => (
            <ListItem key={city}>
              <Stack direction={'row'} gap={1} alignItems="center">
                {city}, {street}
                {actions.map((action) => (
                  <Can I={action} a={type} ability={ability}>
                    <Button size="small">{action}</Button>
                  </Can>
                ))}
              </Stack>
            </ListItem>
          ))}
        </List>
      </ParentCard>
    </PageContainer>
  );
};

export default RollbaseCASL;
