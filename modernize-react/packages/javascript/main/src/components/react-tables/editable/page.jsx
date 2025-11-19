import * as React from 'react';
import {
  TableContainer,
  Table,
  TableRow,
  TableCell,
  TableBody,
  Avatar,
  Typography,
  TableHead,
  Chip,
  Box,
  MenuItem,
  Button,
  Divider,
  IconButton,
  TextField,
  Select,
} from '@mui/material';
import { Grid } from '@mui/material';
import { Stack } from '@mui/system';
import DownloadCard from 'src/components/shared/DownloadCard';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';

import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  createColumnHelper,
} from '@tanstack/react-table';
import img1 from 'src/assets/images/profile/user-1.jpg';
import img2 from 'src/assets/images/profile/user-2.jpg';
import img3 from 'src/assets/images/profile/user-3.jpg';
import img4 from 'src/assets/images/profile/user-4.jpg';
import img5 from 'src/assets/images/profile/user-5.jpg';
import img6 from 'src/assets/images/profile/user-6.jpg';

export const basicsTableData = [
  {
    id: 1,
    status: 'active',
    avatar: img1,
    name: 'Olivia Rhye',
    project: 'Xtreme admin',
    percent: 60,
  },
  {
    id: 2,
    status: 'cancel',
    avatar: img2,
    name: 'Barbara Steele',
    project: 'Adminpro admin',
    percent: 30,
  },
  {
    id: 3,
    status: 'pending',
    avatar: img3,
    name: 'Isabel Vasquez',
    project: 'Modernize admin',
    percent: 32,
  },
  {
    id: 4,
    status: 'active',
    avatar: img4,
    name: 'Olivia Rhye',
    project: 'Xtreme admin',
    percent: 60,
  },
  {
    id: 5,
    status: 'cancel',
    avatar: img5,
    name: 'Barbara Steele',
    project: 'Adminpro admin',
    percent: 30,
  },
  {
    id: 6,
    status: 'active',
    avatar: img6,
    name: 'Leonard Gordon',
    project: 'Monster admin',
    percent: 45,
  },
  {
    id: 7,
    status: 'pending',
    avatar: img4,
    name: 'Evelyn Pope',
    project: 'Materialpro admin',
    percent: 37,
  },
  {
    id: 8,
    status: 'active',
    avatar: img6,
    name: 'Leonard Gordon',
    project: 'Monster admin',
    percent: 45,
  },
  {
    id: 9,
    status: 'pending',
    avatar: img5,
    name: 'Evelyn Pope',
    project: 'Materialpro admin',
    percent: 37,
  },
  {
    id: 10,
    status: 'cancel',
    avatar: img1,
    name: 'Tommy Garza',
    project: 'Elegant admin',
    percent: 87,
  },
];

const statusOptions = [
  { value: 'active', label: 'Active' },
  { value: 'cancel', label: 'Cancel' },
  { value: 'pending', label: 'Pending' },
];

const columnHelper = createColumnHelper();

const columns = [
  columnHelper.accessor('name', {
    header: () => 'User',
    cell: (info) => (
      <Stack direction="row" alignItems="center" spacing={2}>
        <Avatar
          src={info.row.original.avatar}
          alt={info.row.original.avatar}
          sx={{ width: 42, height: 42 }}
        />
        <Box>
          <Typography variant="h6">{info.getValue()}</Typography>
        </Box>
      </Stack>
    ),
  }),
  columnHelper.accessor('project', {
    header: () => 'Project Name',
    cell: (info) => (
      <Typography variant="subtitle1" color="textSecondary">
        {info.getValue()}
      </Typography>
    ),
  }),

  columnHelper.accessor('status', {
    header: () => 'Status',
    meta: {
      filterVariant: 'select',
    },
    cell: (info) => (
      <Chip
        sx={{
          bgcolor:
            info.getValue() === 'active'
              ? (theme) => theme.palette.success.light
              : info.getValue() === 'pending'
                ? (theme) => theme.palette.warning.light
                : info.getValue() === 'completed'
                  ? (theme) => theme.palette.primary.light
                  : info.getValue() === 'cancel'
                    ? (theme) => theme.palette.error.light
                    : (theme) => theme.palette.secondary.light,
          color:
            info.getValue() === 'active'
              ? (theme) => theme.palette.success.main
              : info.getValue() === 'pending'
                ? (theme) => theme.palette.warning.main
                : info.getValue() === 'completed'
                  ? (theme) => theme.palette.primary.main
                  : info.getValue() === 'cancel'
                    ? (theme) => theme.palette.error.main
                    : (theme) => theme.palette.secondary.main,
          borderRadius: '8px',
        }}
        label={info.getValue()}
      />
    ),
  }),
  columnHelper.accessor('edit', {
    header: () => 'edit',
    cell: ({ row }) => (
      <Button onClick={() => row.getToggleExpandedHandler()}>
        <EditIcon />
      </Button>
    ),
  }),
];

const EditableTable = () => {
  const [data, _setData] = React.useState(() => [...basicsTableData]);
  const [editRowId, setEditRowId] = React.useState(null);
  const [editedData, setEditedData] = React.useState(null);

  const rerender = React.useReducer(() => ({}), {})[1];
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  //edit
  const handleEdit = (row) => {
    setEditRowId(row.id);
    setEditedData({ ...row });
  };

  const handleSave = () => {
    if (editedData) {
      _setData(data.map((item) => (item.id === editedData.id ? editedData : item)));
      setEditRowId(null);
      setEditedData(null);
    }
  };

  const handleChange = (e, field) => {
    if (editedData) {
      setEditedData({
        ...editedData,
        [field]: e.target.value,
      });
    }
  };

  const handleDownload = () => {
    const headers = ['Users', 'Project Name', 'Status', 'percent'];
    const rows = data.map((item) => [item.name, item.project, item.status, item.percent]);

    const csvContent = [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'table-data.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  return (
    <DownloadCard title="Editable Table" onDownload={handleDownload}>
      <Grid container spacing={3}>
        <Grid size={12}>
          <Box>
            <TableContainer>
              <Table
                sx={{
                  whiteSpace: 'nowrap',
                }}
              >
                <TableHead>
                  {table.getHeaderGroups().map((headerGroup) => (
                    <TableRow key={headerGroup.id}>
                      {headerGroup.headers.map((header) => (
                        <TableCell key={header.id}>
                          <Typography variant="h6">
                            {header.isPlaceholder
                              ? null
                              : flexRender(header.column.columnDef.header, header.getContext())}
                          </Typography>
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableHead>
                <TableBody>
                  {table.getRowModel().rows.map((row) => (
                    <TableRow key={row.id}>
                      {row.getVisibleCells().map((cell) => (
                        <TableCell key={cell.id}>
                          {cell.column.id === 'edit' ? (
                            editRowId === row.original.id ? (
                              <>
                                <IconButton onClick={handleSave} color="primary">
                                  <CheckIcon />
                                </IconButton>
                                <IconButton onClick={() => setEditRowId(null)} color="error">
                                  <CloseIcon />
                                </IconButton>
                              </>
                            ) : (
                              <IconButton onClick={() => handleEdit(row.original)} color="primary">
                                <EditIcon />
                              </IconButton>
                            )
                          ) : editRowId === row.original.id ? (
                            cell.column.id === 'status' ? (
                              <Select
                                value={editedData?.status || ''}
                                onChange={(e) => handleChange(e, 'status')}
                                variant="outlined"
                                fullWidth
                              >
                                {statusOptions.map((option) => (
                                  <MenuItem key={option.value} value={option.value}>
                                    {option.label}
                                  </MenuItem>
                                ))}
                              </Select>
                            ) : (
                              <TextField
                                variant="outlined"
                                value={editedData?.[cell.column.id] || ''}
                                onChange={(e) => handleChange(e, cell.column.id)}
                                fullWidth
                              />
                            )
                          ) : (
                            flexRender(cell.column.columnDef.cell, cell.getContext())
                          )}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Divider />
          </Box>
        </Grid>
      </Grid>
    </DownloadCard>
  );
};
export default EditableTable;
