// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';

import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import TiptapEdit from './TiptapEdit';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Tiptap Editor',
  },
];

const TiptapEditor = () => {
  return (
    <PageContainer title="Tiptap Editor" description="this is Tiptap Editor page">
      {/* breadcrumb */}
      <Breadcrumb title="Tiptap Editor" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Tiptap Editor">
        <TiptapEdit />
      </ParentCard>
    </PageContainer>
  );
};

export default TiptapEditor;

