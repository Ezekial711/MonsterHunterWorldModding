# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 03:14:10 2021

@author: AsteriskAmpersand
"""
import re

def createCT(name,entryList):
    entryPattern = """
            <CheatEntry>
              <ID>1</ID>
              <Description>"%s"</Description>
              <VariableType>%s</VariableType>
              <Address>+%s</Address>
            </CheatEntry>"""
    entries = ''.join((entryPattern%entry for entry in entryList))
    return """
<?xml version="1.0" encoding="utf-8"?>
<CheatTable CheatEngineTableVersion="31">
  <CheatEntries>
    <CheatEntry>
      <ID>30</ID>
      <Description>"%s"</Description>
      <Options moHideChildren="1"/>
      <LastState Value="" RealAddress="862E0AA0"/>
      <GroupHeader>1</GroupHeader>
      <Address>862E0AA0</Address>
      <CheatEntries>
        <CheatEntry>
          <ID>0</ID>
          <Description>"Class"</Description>
          <ShowAsHex>1</ShowAsHex>
          <VariableType>Array of byte</VariableType>
          <ByteLength>8</ByteLength>
          <Address>+0</Address>
        </CheatEntry>          
%s
      </CheatEntries>
    </CheatEntry>
  </CheatEntries>
  <UserdefinedSymbols/>
</CheatTable>
    
    
    """%(name,entries)

commentPattern = re.compile(r"// [a-zA-Z0-9:]* vftable:([0-9A-Fx]*)")
classPattern = re.compile(r".*class\s+([a-zA-Z0-9:]*)")
entryPattern = re.compile(r"\s*([a-zA-Z0-9]*)\s*'(.*)'.*Offset:([0-9A-Fx]*)" )
endPattern = re.compile(r" };")

typings = {"f64" : "Double",
           "f32" : "Float",
           "u64" : "8 Bytes",
           "s64" : "8 Bytes",
           "u32" : "4 Bytes",
           "s32" : "4 Bytes",
           "u16" : "2 Bytes",
           "s16" : "2 Bytes",
           "u8" : "Byte",
           "s8" : "Byte",
           "matrix44" : "Float",
           "vector3" : "Float",
           "bool" : "Byte",
           "string" : "String"
           }

def parseTyping(typing):
    if typing not in typings:
        return "4 Bytes"
    else:
        return typings[typing]

def parseEntries(dataDumpClass):
    started = False
    entries = []
    comment = ""
    for line in dataDumpClass:
        if not started:
            commentMatch = commentPattern.match(line)
            if commentMatch:
                comment = " ["+commentMatch[1]+"]"
            classMatch = classPattern.match(line)
            if classMatch:
                name = classMatch[1]+comment
                started = True
        if started: 
            entryMatch = entryPattern.match(line)
            if entryMatch:
                description = entryMatch[2]
                typing = parseTyping(entryMatch[1])
                offset = entryMatch[3]
                if offset == "0x7FFFFFFFFFFFFFFF":
                    offset = "0x0"
                    description += " [INVALID ENTRY]"
                if entryMatch[1] == "matrix44":
                    for i in range(4):
                        for j in range(4):
                            entries.append((description+"%d%d"%(i,j),typing,hex(int(offset,16)+4*(j+4*i))[2:]))
                elif entryMatch[1] == "vector3":
                    for i in range(3):
                        entries.append((description+"%d"%i,typing,hex(int(offset,16)+4*i)[2:]))
                else:
                    entries.append((description,typing,offset[2:]))
            endMatch = endPattern.match(line)
            if endMatch:
                break
    return name, entries        
