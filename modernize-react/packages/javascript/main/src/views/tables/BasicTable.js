import React from 'react';
import {
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Avatar,
  AvatarGroup,
  Chip,
  Paper,
  TableContainer,
  Stack,
} from '@mui/material';

import Breadcrumb from '../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../components/container/PageContainer';
import { basicsTableData } from './tableData';

import ParentCard from '../../components/shared/ParentCard';

const basics = basicsTableData;
const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Basic Table',
  },
];

const BasicTable = () => (
  <PageContainer title="Basic Table" description="this is Basic Table page">
    {/* breadcrumb */}
    <Breadcrumb title="Basic Table" items={BCrumb} />
    {/* end breadcrumb */}
    <ParentCard title="Basic Table">
      <Paper variant="outlined">
        <TableContainer >
          <Table
            aria-label="simple table"
            sx={{
              whiteSpace: 'nowrap',
            }}
          >
            <TableHead>
              <TableRow>
                <TableCell>
                  <Typography variant="h6">Users</Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="h6">Project Name</Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="h6">Team</Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="h6">Status</Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="h6">Budget</Typography>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {basics.map((basic) => (
                <TableRow key={basic.id}>
                  <TableCell>
                    <Stack direction="row" spacing={2}>
                      <Avatar src={basic.imgsrc} alt={basic.imgsrc} width="35" />
                      <Box>
                        <Typography variant="h6" fontWeight="600">
                          {basic.name}
                        </Typography>
                        <Typography color="textSecondary" variant="subtitle2">
                          {basic.post}
                        </Typography>
                      </Box>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Typography color="textSecondary" variant="h6" fontWeight="400">
                      {basic.pname}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row">
                      <AvatarGroup max={4}>
                        {basic.teams.map((team) => (
                          <Avatar
                            key={team.id}
                            width="35"
                            sx={{
                              bgcolor: team.color,
                            }}
                          >
                            {team.text}
                          </Avatar>
                        ))}
                      </AvatarGroup>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    {/* <Chip chipcolor={basic.status == 'Active' ? 'success' : basic.status == 'Pending' ? 'warning' : basic.status == 'Completed' ? 'primary' : basic.status == 'Cancel' ? 'error' : 'secondary'} */}
                    <Chip
                      sx={{
                        bgcolor:
                          basic.status === 'Active'
                            ? (theme) => theme.palette.success.light
                            : basic.status === 'Pending'
                              ? (theme) => theme.palette.warning.light
                              : basic.status === 'Completed'
                                ? (theme) => theme.palette.primary.light
                                : basic.status === 'Cancel'
                                  ? (theme) => theme.palette.error.light
                                  : (theme) => theme.palette.secondary.light,
                        color:
                          basic.status === 'Active'
                            ? (theme) => theme.palette.success.main
                            : basic.status === 'Pending'
                              ? (theme) => theme.palette.warning.main
                              : basic.status === 'Completed'
                                ? (theme) => theme.palette.primary.main
                                : basic.status === 'Cancel'
                                  ? (theme) => theme.palette.error.main
                                  : (theme) => theme.palette.secondary.main,
                        borderRadius: "8px"
                      }}
                      size="small"
                      label={basic.status}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="h6">${basic.budget}k</Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </ParentCard>
  </PageContainer>
);

export default BasicTable;
