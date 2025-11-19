
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
  Grid,
  MenuItem,
  Button,
  Divider,
  IconButton,
  AvatarGroup,
} from '@mui/material';
import { Stack } from '@mui/system';
import DownloadCard from 'src/components/shared/DownloadCard';
import { basicsTableData, PaginationDataType } from './PaginationData';

import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  createColumnHelper,
} from '@tanstack/react-table';
import CustomTextField from 'src/components/forms/theme-elements/CustomTextField';
import CustomSelect from 'src/components/forms/theme-elements/CustomSelect';
import {
  IconChevronLeft,
  IconChevronRight,
  IconChevronsLeft,
  IconChevronsRight,
} from '@tabler/icons-react';

const basics = basicsTableData;

const columnHelper = createColumnHelper<PaginationDataType>();

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
  columnHelper.accessor('users', {
    header: () => 'Users',
    cell: (info) => (
      <AvatarGroup sx={{ justifyContent: 'start' }}>
        {info.getValue().map((user, i) => (
          <Avatar src={user.img} alt={user.img} key={i} sx={{ width: 35, height: 35 }} />
        ))}
      </AvatarGroup>
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
];

const ReactPaginationTable = () => {
  const [data, _setData] = React.useState(() => [...basics]);
  const [columnFilters, setColumnFilters] = React.useState<any>([]);
  const rerender = React.useReducer(() => ({}), {})[1];

  const table = useReactTable({
    data,
    columns,
    filterFns: {},
    state: {
      columnFilters,
    },
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(), //client side filtering
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    debugTable: true,
    debugHeaders: true,
    debugColumns: false,
  });

  const handleDownload = () => {
    const headers = ['avatar', 'name', 'project', 'percent', 'status', 'users'];
    const rows = data.map((item) => [
      item.name,
      item.project,
      item.percent,
      item.status,
      item.avatar,
      item.users.map((user) => user.img).join(','),
    ]);

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
    (<DownloadCard title="Pagination Table" onDownload={handleDownload}>
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
                          <Typography
                            variant="h6"
                            mb={1}
                            className={
                              header.column.getCanSort() ? 'cursor-pointer select-none' : ''
                            }
                            onClick={header.column.getToggleSortingHandler()}
                          >
                            {header.isPlaceholder
                              ? null
                              : flexRender(header.column.columnDef.header, header.getContext())}
                            {(() => {
                              const sortState = header.column.getIsSorted();
                              if (sortState === 'asc') return ' 🔼';
                              if (sortState === 'desc') return ' 🔽';
                              return null;
                            })()}
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
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Divider />
            <Stack
              gap={1}
              p={3}
              alignItems="center"
              direction={{ xs: 'column', sm: 'row' }}
              justifyContent="space-between"
            >
              <Box display="flex" alignItems="center" gap={1}>
                <Button variant="contained" color="primary" onClick={() => rerender()}>
                  Force Rerender
                </Button>
                <Typography variant="body1">
                  {table.getPrePaginationRowModel().rows.length} Rows
                </Typography>
              </Box>
              <Box
                sx={{
                  display: {
                    xs: 'block',
                    sm: 'flex',
                  },
                }}
                alignItems="center"
                gap={1}
              >
                <Stack direction="row" alignItems="center" gap={1}>
                  <Typography variant="body1">Page</Typography>
                  <Typography variant="body1" fontWeight={600}>
                    {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
                  </Typography>
                </Stack>
                <Stack direction="row" alignItems="center" gap={1}>
                  | Go to page:
                  <CustomTextField
                    type="number"
                    min="1"
                    max={table.getPageCount()}
                    defaultValue={table.getState().pagination.pageIndex + 1}
                    onChange={(e: { target: { value: any } }) => {
                      const page = e.target.value ? Number(e.target.value) - 1 : 0;
                      table.setPageIndex(page);
                    }}
                  />
                </Stack>
                <CustomSelect
                  value={table.getState().pagination.pageSize}
                  onChange={(e: { target: { value: any } }) => {
                    table.setPageSize(Number(e.target.value));
                  }}
                >
                  {[10, 15, 20, 25].map((pageSize) => (
                    <MenuItem key={pageSize} value={pageSize}>
                      {pageSize}
                    </MenuItem>
                  ))}
                </CustomSelect>

                <IconButton
                  size="small"
                  onClick={() => table.setPageIndex(0)}
                  disabled={!table.getCanPreviousPage()}
                >
                  <IconChevronsLeft />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => table.previousPage()}
                  disabled={!table.getCanPreviousPage()}
                >
                  <IconChevronLeft />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => table.nextPage()}
                  disabled={!table.getCanNextPage()}
                >
                  <IconChevronRight />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                  disabled={!table.getCanNextPage()}
                >
                  <IconChevronsRight />
                </IconButton>
              </Box>
            </Stack>
          </Box>
        </Grid>
      </Grid>
    </DownloadCard>)
  );
};

export default ReactPaginationTable;
