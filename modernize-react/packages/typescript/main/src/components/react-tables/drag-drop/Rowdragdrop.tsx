
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
  AvatarGroup,
  Grid,
} from '@mui/material';
import { Stack } from '@mui/system';
import DownloadCard from 'src/components/shared/DownloadCard';
import { basicsTableData, EnTableType } from 'src/components/tables/tableData';
import {
  DndContext,
  MouseSensor,
  TouchSensor,
  KeyboardSensor,
  closestCenter,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
  arrayMove,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { IconGripVertical } from '@tabler/icons-react';

const basics = basicsTableData;

const columnHelper = createColumnHelper<EnTableType>();

const columns = [
  columnHelper.accessor('dragHandle', {
    cell: () => (
      <span>
        <IconGripVertical size={18} />
      </span>
    ),
    header: () => <span></span>,
  }),

  columnHelper.accessor('imgsrc', {
    header: () => 'Users',
    cell: (info) => (
      <Stack direction="row" spacing={2}>
        <Avatar src={info.getValue()} alt={info.getValue()} sx={{ width: 40, height: 40 }} />
        <Box>
          <Typography variant="h6" fontWeight="600">
            {info.row.original.name}
          </Typography>
          <Typography color="textSecondary" variant="subtitle2">
            {info.row.original.post}
          </Typography>
        </Box>
      </Stack>
    ),
  }),
  columnHelper.accessor('pname', {
    header: () => 'Project Name',
    cell: (info) => (
      <Typography color="textSecondary" variant="h6" fontWeight={400}>
        {info.row.original.pname}
      </Typography>
    ),
  }),
  columnHelper.accessor('teams', {
    header: () => 'Team',
    cell: (info) => (
      <Stack direction="row">
        <AvatarGroup max={4}>
          {info.getValue().map((team) => (
            <Avatar
              key={team.id}
              sx={{
                bgcolor: team.color,
                width: 35,
                height: 35,
              }}
            >
              {team.text}
            </Avatar>
          ))}
        </AvatarGroup>
      </Stack>
    ),
  }),
  columnHelper.accessor('status', {
    header: () => 'Status',
    cell: (info) => (
      <Chip
        sx={{
          bgcolor:
            info.getValue() === 'Active'
              ? (theme) => theme.palette.success.light
              : info.getValue() === 'Pending'
                ? (theme) => theme.palette.warning.light
                : info.getValue() === 'Completed'
                  ? (theme) => theme.palette.primary.light
                  : info.getValue() === 'Cancel'
                    ? (theme) => theme.palette.error.light
                    : (theme) => theme.palette.secondary.light,
          color:
            info.getValue() === 'Active'
              ? (theme) => theme.palette.success.main
              : info.getValue() === 'Pending'
                ? (theme) => theme.palette.warning.main
                : info.getValue() === 'Completed'
                  ? (theme) => theme.palette.primary.main
                  : info.getValue() === 'Cancel'
                    ? (theme) => theme.palette.error.main
                    : (theme) => theme.palette.secondary.main,
          borderRadius: '8px',
        }}
        size="small"
        label={info.getValue()}
      />
    ),
  }),
  columnHelper.accessor('budget', {
    header: () => 'Budget',
    cell: (info) => <Typography variant="h6">${info.row.original.budget}k</Typography>,
  }),
];

const DraggableRow = ({ row }: any) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: row.original.id,
  });

  const style: any = {
    transform: CSS.Translate.toString(transform),
    transition,
    cursor: 'move',
  };

  return (
    <TableRow ref={setNodeRef} style={style} {...attributes} {...listeners}>
      {row.getVisibleCells().map((cell: any) => (
        <TableCell key={cell.id}>
          {flexRender(cell.column.columnDef.cell, cell.getContext())}
        </TableCell>
      ))}
    </TableRow>
  );
};

const Rowdragdrop = () => {
  const [data, _setData] = React.useState<any>(() => [...basics]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });
  const handleDragEnd = (event: { active: any; over: any }) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      _setData((prevData: any[]) => {
        const oldIndex = prevData.findIndex((item) => item.id === active.id);
        const newIndex = prevData.findIndex((item) => item.id === over?.id);
        return arrayMove(prevData, oldIndex, newIndex);
      });
    }
  };

  const sensors = useSensors(
    useSensor(MouseSensor),
    useSensor(TouchSensor),
    useSensor(KeyboardSensor),
  );

  const handleDownload = () => {
    const headers = ['Users', 'Project Name', 'Team', 'Status', 'Budget'];
    const rows = data.map(
      (item: { name: any; pname: any; teams: any[]; status: any; budget: any }) => [
        item.name,
        item.pname,
        item.teams.map((team: { text: any }) => team.text).join(', '),
        item.status,
        item.budget,
      ],
    );

    const csvContent = [headers.join(','), ...rows.map((e: any[]) => e.join(','))].join('\n');

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
    (<DndContext onDragEnd={handleDragEnd} sensors={sensors} collisionDetection={closestCenter}>
      <DownloadCard title="Row Drag & Drop Table" onDownload={handleDownload}>
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
                    <SortableContext
                      items={data.map((row: { id: any }) => row.id)}
                      strategy={verticalListSortingStrategy}
                    >
                      {table.getRowModel().rows.map((row) => (
                        <DraggableRow key={row.id} row={row} />
                      ))}
                    </SortableContext>
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </Grid>
        </Grid>
      </DownloadCard>
    </DndContext>)
  );
};
export default Rowdragdrop;
