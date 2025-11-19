// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import {
  MenuButtonBold,
  MenuButtonItalic,
  MenuControlsContainer,
  MenuDivider,
  MenuSelectHeading,
  RichTextEditorProvider,
  RichTextField,
  MenuButtonStrikethrough,
  MenuButtonOrderedList,
  MenuButtonBulletedList,
  MenuButtonBlockquote,
  MenuButtonCode,
  MenuButtonHorizontalRule,
  MenuButtonUndo,
  MenuButtonRedo,
  MenuButtonRemoveFormatting,
} from "mui-tiptap";
import './Tiptap.css';


const TiptapEdit = () => {

  const editor = useEditor({
    extensions: [StarterKit],
    content: "<p>Type here...</p>",
  });



  return (

    <RichTextEditorProvider editor={editor} >
      <RichTextField
        controls={
          <MenuControlsContainer>
            <MenuSelectHeading />
            <MenuDivider />
            <MenuButtonBold />
            <MenuButtonItalic />

            <MenuButtonStrikethrough />
            <MenuDivider />

            <MenuButtonOrderedList />
            <MenuButtonBulletedList />
            <MenuDivider />
            <MenuButtonBlockquote />
            <MenuButtonCode />
            <MenuButtonHorizontalRule />
            <MenuDivider />

            <MenuButtonUndo />
            <MenuButtonRedo />
            <MenuDivider />

            <MenuButtonRemoveFormatting />

          </MenuControlsContainer>
        }

      />
    </RichTextEditorProvider>

  );
};
export default TiptapEdit;
