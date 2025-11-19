
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
  IconButton,
} from '@mui/material';
import { Stack } from '@mui/system';
import {
  DndContext,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  closestCenter,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import { SortableContext, horizontalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import DownloadCard from 'src/components/shared/DownloadCard';
import { basicsTableData, EnTableType } from 'src/components/tables/tableData';
import { CSS } from '@dnd-kit/utilities';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { IconGripHorizontal } from '@tabler/icons-react';

const basics = basicsTableData;

const columnHelper = createColumnHelper<EnTableType>();

const columns = [
  columnHelper.accessor('imgsrc', {
    id: 'imgsrc',
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
    id: 'pname',
    header: () => 'Project Name',
    cell: (info) => (
      <Typography color="textSecondary" variant="h6" fontWeight={400}>
        {info.row.original.pname}
      </Typography>
    ),
  }),
  columnHelper.accessor('teams', {
    id: 'teams',
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
    id: 'status',
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
    id: 'budget',
    header: () => 'Budget',
    cell: (info) => <Typography variant="h6">${info.row.original.budget}</Typography>,
  }),
];

const arrayMove = (array: any, from: any, to: any) => {
  const item = array[from];
  const newArray = array.slice();
  newArray.splice(from, 1);
  newArray.splice(to, 0, item);
  return newArray;
};
const DraggableTableHeader = ({ header }: any) => {
  const { attributes, isDragging, listeners, setNodeRef, transform } = useSortable({
    id: header.id,
  });

  const style: any = {
    opacity: isDragging ? 0.8 : 1,
    position: 'relative',
    transform: CSS.Translate.toString(transform),
    transition: 'width transform 0.2s ease-in-out',
    whiteSpace: 'nowrap',
    width: header.column.getSize(),
    zIndex: isDragging ? 1 : 0,
    textAlign: 'left',
    padding: '0 16px',
  };

  return (
    <th ref={setNodeRef} style={style} {...attributes} {...listeners}>
      {header.isPlaceholder
        ? null
        : flexRender(header.column.columnDef.header, header.getContext())}
      <IconButton size="small" {...attributes} {...listeners}>
        <IconGripHorizontal size={18} />
      </IconButton>
    </th>
  );
};
const DragAlongCell = ({ cell }: any) => {
  const { isDragging, setNodeRef, transform } = useSortable({
    id: cell.column.id,
  });

  const style: any = {
    opacity: isDragging ? 0.8 : 1,
    position: 'relative',
    transform: CSS.Translate.toString(transform),
    transition: 'width transform 0.2s ease-in-out',
    width: cell.column.getSize(),
    zIndex: isDragging ? 1 : 0,

  };

  return (
    <TableCell style={style} ref={setNodeRef} className="whitespace-nowrap py-3 px-4">
      {flexRender(cell.column.columnDef.cell, cell.getContext())}
    </TableCell>
  );
};

const Columndragdrop = () => {
  const [data, _setData] = React.useState<any>(() => [...basics]);
  const [columnOrder, setColumnOrder] = React.useState<any>(columns.map((c) => c.id));

  const table = useReactTable({
    data,
    columns,
    state: {
      columnOrder,
    },
    onColumnOrderChange: setColumnOrder,
    getCoreRowModel: getCoreRowModel(),
    debugColumns: true,
    debugTable: true,
    debugHeaders: true,
  });

  const handleDragEnd = (event: { active: any; over: any }) => {
    const { active, over } = event;
    if (active && over && active.id !== over.id) {
      setColumnOrder((columnOrder: string | any[]) => {
        const oldIndex = columnOrder.indexOf(active.id);
        const newIndex = columnOrder.indexOf(over.id);
        return arrayMove(columnOrder, oldIndex, newIndex);
      });
    }
  };

  const sensors = useSensors(
    useSensor(MouseSensor, {}),
    useSensor(TouchSensor, {}),
    useSensor(KeyboardSensor, {}),
  );

  const handleDownload = () => {
    const headers = ['Users', 'Project Name', 'Team', 'Status', 'Budget'];
    const rows = data.map(
      (item: { name: any; pname: any; teams: any[]; status: any; budget: any }) => [
        item.name,
        item.pname,
        item.teams.map((team) => team.text).join(', '),
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
    (<DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd} sensors={sensors}>
      <DownloadCard title="Column drag & drop Table" onDownload={handleDownload}>
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
                        <SortableContext
                          items={columnOrder}
                          strategy={horizontalListSortingStrategy}
                        >
                          {headerGroup.headers.map((header) => (
                            <DraggableTableHeader key={header.id} header={header} />
                          ))}
                        </SortableContext>
                      </TableRow>
                    ))}
                  </TableHead>
                  <TableBody>
                    {table.getRowModel().rows.map((row) => (
                      <TableRow key={row.id}>
                        {row.getVisibleCells().map((cell) => (
                          <SortableContext
                            key={cell.id}
                            items={columnOrder}
                            strategy={horizontalListSortingStrategy}
                          >
                            <DragAlongCell key={cell.id} cell={cell} />
                          </SortableContext>
                        ))}
                      </TableRow>
                    ))}
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

export default Columndragdrop;
